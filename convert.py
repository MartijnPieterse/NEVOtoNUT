# Convert NEVO to ASDA nutrition format.
# -*- coding: iso-8859-15 -*-


nutrient_list = {}

f = open("data/Nevo-Nutrienten_Lijst_Online versie 2011_3.0.txt")

for l in f.readlines():
    code = l[0:5]
    name = l[7:37].rstrip()
    meeteenheid = l[39:44].rstrip()
    english_name = l[49:80].rstrip()        # Thrown away.

    nutrient_list[code] = {"name": name, "unit": meeteenheid }

f.close()


conversion_table = []

f = open("nut.txt")
fdef = open("data/NUTR_DEF.txt") # To verify units are the same.

for l in f.readlines():

    v = fdef.readline()
    v_unit = v.split("^")[1].strip("~")

    if v_unit == "µg": v_unit = "ug"

    if l[0] == "~": conversion_table.append("-0")       # No data.
    elif l[0] == "!":
        conversion_table.append(l.strip())
    else:
        code = l[0:5]

        if nutrient_list[code]["unit"] == "%":
            # Convert to "g" later.
            conversion_table.append(code)
        elif nutrient_list[code]["unit"] != v_unit:
            raise "Unit Error"
        else:
            conversion_table.append(code)

f.close()

f = open("data/Nevo-Online versie 2011_3.0.dat")
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
            if t[1] == "1": # Simple addition
                # All others.
                calc = t[3:].split("+")
                
                # TODO What if something is not available?
                total = 0.0
                for c in calc:
                    if r["nut"].has_key(c): total += float(r["nut"][c])

                if total != 0.0: 
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")

            elif t[1] == "2": # Simple multiplication
                calc = t[3:].split("*")

                total = 0.0
                if r["nut"].has_key(calc[0]): total += float(r["nut"][calc[0]])

                total *= float(calc[1])

                if total != 0.0:
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")

            elif t[1] == "3": # multiple multiply/add
                calc = t[3:].split("+")

                total = 0.0
                for c in calc:
                    nut_key = c.split("*")[0]
                    multiply = float(c.split("*")[1])
                    n = 0.0
                    if r["nut"].has_key(nut_key): n = float(r["nut"][nut_key])

                    total += n * multiply

                if total != 0.0:
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")

            elif t[1] == "5": # take % of 03002
                nut_key = t[3:8]

                total = 0.0
                if r["nut"].has_key(nut_key):
                    perc = float(r["nut"][nut_key])

                    total = perc * float(r["nut"]["03002"])

                if total != 0.0:
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")

            elif t[1] == "6": # Simple addition
                calc = t[3:].split("+")
                
                # TODO What if something is not available?
                perc = 0.0
                for c in calc:
                    if r["nut"].has_key(c): perc += float(r["nut"][c])

                if perc != 0.0: 
                    total = perc * float(r["nut"]["03002"])
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")



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



