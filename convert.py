# Convert NEVO to ASDA nutrition format.
# -*- coding: iso-8859-15 -*-


nutrient_list = {}

f = open("Nevo-Nutrienten_Lijst_Online versie 2011_3.0.txt")

for l in f.readlines():
    code = l[0:5]
    name = l[7:37].rstrip()
    meeteenheid = l[39:44].rstrip()
    english_name = l[49:80].rstrip()        # Thrown away.

    nutrient_list[code] = {"name": name, "unit": meeteenheid }

f.close()


conversion_table = []

f = open("nutlight.txt")
fdef = open("NUTR_DEF.txt") # To verify units are the same.

for l in f.readlines():

    v = fdef.readline()
    v_unit = v.split("^")[1].strip("~")

    if v_unit == "�g": v_unit = "ug"

    if l[0] == "~": conversion_table.append("-0")       # No data.
    elif l[0] == "!":
        conversion_table.append(l.strip())
    else:
        code = l[0:5]

        if nutrient_list[code]["unit"] == "%":
            # Convert to "g"
            conversion_table.append(code)
        elif nutrient_list[code]["unit"] != v_unit:
            raise "Unit Error"
        else:
            conversion_table.append(code)

f.close()

f = open("Nevo-Online versie 2011_3.0.dat")
#f = open("/tmp/30.dat")

l = f.readline().strip()
header = False


def printFoodRecord(r):

    # Use empty range from sr25.nut (50000 - 60000)
    s = ""
    s += repr(int(r["Productcode"])+50000) + "^"
    s += r["Productgroepcode"] + "^"
    if len(r["Fabrikantnaam"]) != 0:
        s += r["Fabrikantnaam"] + ","
    s += r["Productgroep-oms"].upper() + "," + r["Product_omschrijving"].upper() + "^"

    s += "^"    # Skip scientific name

    if (r["Eetbaar_gedeelte"] == "1"):
        s += "^"
    else:
        s += repr(int(round(100*(1.0 - float(r["Eetbaar_gedeelte"]))))) + "^"

    # Calories / gram of protein
    # Calories / gram of fat
    # Calories / gram of carbs
    # Empty for now...

    s += "^^^"

    # Now for the big translation
    for t in conversion_table:
        if t == "-0": s += "-0"
        elif t[0] == "!":
            t = t.split("$")[0]
            if (t == "!!11021+11022"):
                # special case for numer 44. (no %)
                total = 0.0
                if r["nut"].has_key("11021"): total += float(r["nut"]["11021"])
                if r["nut"].has_key("11022"): total += float(r["nut"]["11022"])

                if total != 0.0: s += ("%.3f" % (total)).rstrip("0").rstrip(".")
            else:
                # All others.
                calc = t.lstrip("!").split("+")
                
                total = 0.0
                for c in calc:
                    if r["nut"].has_key(c): total += float(r["nut"][c])

                if total != 0.0: 
                    g = float(r["nut"]["03002"]) * total * 0.01
                    s += ("%.3f" % (g)).rstrip("0").rstrip(".")


        elif r["nut"].has_key(t):
            if float(r["nut"][t]) == 0.0:
                pass
            else:
                if nutrient_list[t]["unit"] == "%":
                    if r["nut"].has_key("03002"):
                        g = float(r["nut"]["03002"]) * float(r["nut"][t]) * 0.01
                        s += ("%.3f" % (g)).rstrip("0").rstrip(".")
                    else: raise "Geen 03002!"
                else: s += r["nut"][t]
        else: s += "-0"

        s += "^"
    

    # Last 3 fields. Now just 1 serving == 100g
    s += "1^100g^100"
    print s


foodrecord = None
while len(l) != 0:
    if header:
        if l.find("Nutrientcode") == 0:

            foodrecord["nut"] = {}
            header = False
            # skip next line.
            f.readline()
        else:
            foodrecord[l[0:24].rstrip()] = l[24:]

    else:
        if l == "----------":

            if foodrecord != None: printFoodRecord(foodrecord)
            foodrecord = {}
            header = True
        else:
            # We have a nutrient! Fill the record.
            code = l[0:5]
            gehalte = l[11:21].strip()
            broncode = l[23:24].rstrip()
            mutatie = l[40:49].rstrip()
            spoor = l[51:52].rstrip()


            foodrecord["nut"][code] = gehalte

    l = f.readline().strip()

f.close()



