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

    # Alway add NEVO, to make it easier to know what is dutch
    name = "NEVO,"
#    if len(r["Fabrikantnaam"]) != 0:
#        name += r["Fabrikantnaam"].upper() + ","
    name += r["Productgroep-oms"].upper() + "," + r["Product_omschrijving"].upper()

    name_orig = name

    # Replace some names.
    name = name.replace(", ", ",")
    name = name.replace("VLEES,VLEESWAREN EN GEVOGELTE", "VLEES/GEVOGELTE", 1)
    name = name.replace("VETTEN,OLIëN EN HARTIGE SAUZEN", "VET/OLIE/SAUS", 1)
    name = name.replace("ALCOHOLISCHE EN NIET-ALCOHOLISCHE DRANKEN", "DRANKEN", 1)
    name = name.replace("SOJAPRODUCTEN EN VEGETARISCHE PRODUCTEN", "SOJA EN VEGAPROD", 1)
    name = name.replace("SNOEP,ZOET BELEG EN ZOETE SAUZEN,", "", 1)
    name = name.replace("GRAANPRODUCTEN EN BINDMIDDELEN", "GRAANPROD EN BINDM", 1)
    name = name.replace("SAMENGESTELDE GERECHTEN", "MAALTIJD", 1)
    name = name.replace("ONGEZOUTEN", "ONGEZ.", 1);
    name = name.replace("VET ONGEBONDEN BEREID", "VET ONGEB. BEREID", 1)
    name = name.replace("VET GEBONDEN BEREID", "VET GEB. BEREID", 1)
    name = name.replace("CHOCOLADE MELK-", "MELKCHOCOLADE", 1)
    name = name.replace("TAART APPEL-", "APPELTAART", 1)
    name = name.replace(" EXCL ", " EX ", 1)
    name = name.replace(",ONTBIJTPRODUCT ", ",", 1)
    name = name.replace(",ONTBIJTPROD ", ",", 1)
    name = name.replace("BAK- EN BRAADVET","BAK/BRAADVET", 1)
    name = name.replace("MELK EN MELKPRODUCTEN", "MELKPRODUCTEN", 1)
    name = name.replace("BEREID Z VET BEREID Z VET", "BEREID Z VET", 1)
    name = name.replace("WORSTJES M ITALIAANSE KRUIDEN", "WORSTJES M ITA. KRUIDEN", 1)
    name = name.replace(",GEBAK EN KOEK,", ",GEBAK/KOEK,", 1)
    name = name.replace("VRUCHTENDRANK APPELSIENTJE VITAMIENTJE BOSVRUCHTEN", "APPELSIENTJE VITAMIENTJE BOSVRUCHTEN", 1)
    name = name.replace(" ONBEREID", " ONBER", 1)
    name = name.replace("YOGHURT MAGERE M VRUCHTEN/VANILLE M ZOETST", "MAGERE YOGHURT VRUCHTEN/VANILLE M ZOETST", 1)
    name = name.replace("MARGARINEPRODUCT 70%", "MARGARINE 70%", 1)
    name = name.replace("SAUS WARM", "SAUS ", 1)
    name = name.replace("SAP VRUCHTEN- APPELSIENTJE VITAMIENTJE ORANJE VR", "APPELSIENTJE VITAMIENTJE ORANJE VRUCHTEN", 1)


    # These last ones.. just do manually.
    name = name.replace("NEVO,DRANKEN,FRISDRANK M SUIKER EN ZOETST 2-<5 G KH M CAFEINE", "NEVO,DRANKEN,FRISDRANK M SUIKER EN ZOETST 2-<5 G KH CAFEINE", 1)
    name = name.replace("NEVO,DRANKEN,FRISDRANK M SUIKER EN ZOETST 5-<8 G KH M CAFEINE", "NEVO,DRANKEN,FRISDRANK M SUIKER EN ZOETST 5-<8 G KH CAFEINE", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,BAK/BRAADVET VLOEIB 97% VET <17G VERZ VETZ", "NEVO,VET/OLIE/SAUS,BAK/BRAAD VLOEIB 97% VET <17G VERZ VETZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,SAUS CHINESE ZOETZURE HUISHOUDELIJK BEREID", "NEVO,VET/OLIE/SAUS,SAUS CHINESE ZOETZURE THUIS BEREID", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,SAUS OP BASIS GROENTENAT/MELK BEREID Z VET", "NEVO,VET/OLIE/SAUS,SAUS OP BASIS GROENTENAT/MELK Z VET", 1)
    name = name.replace("NEVO,NOTEN,ZADEN EN SNACKS,KIKKERWTEN GEROOSTERD LEBLEBI TURKS", "NEVO,NOTEN,ZADEN EN SNACKS,KIKKERWTEN GEROOSTERD LEBLEBI", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,DRESSING/SAUS FRITES-/SAUS SLA- CA 13% OLIE", "NEVO,VET/OLIE/SAUS,DRESSING/FRISTESSAUS/SLASAUS CA 13% OLIE", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT 20-25% VET <10 G VERZ VETZ", "NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT 20-25% VET <10 G VERZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,MARGARINE VLOEIBAAR 80% VET <17 G VERZ VETZ", "NEVO,VET/OLIE/SAUS,MARGARINE VLOEIBAAR 80% VET <17 G VERZ", 1)
    name = name.replace("NEVO,AARDAPPELEN,AARDAPPELPUREE INSTANT BEREID M HALFVOLLE MELK", "NEVO,AARDAPPELEN,AARDAPPELPUREE INSTANT BEREID M HALFV MELK", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,MARGARINE VLB 80% VET< 17 G VERZ VETZ ONGEZ.", "NEVO,VET/OLIE/SAUS,MARGARINE VLB 80% VET< 17 G VERZ VETZ ZZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,SAUS SATE- HUISHOUDELIJK BEREID M WATER M VET", "NEVO,VET/OLIE/SAUS,SATESAUS THUIS BEREID M WATER M VET", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,BAK/BRAADVET VLB 97% VET <17G VERZ VETZ ONGEZ.", "NEVO,VET/OLIE/SAUS,BAK/BRAADVET 97% VET <17G VERZ VETZ ZZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT 35% VET <10G VERZ VETZ ONGEZ.", "NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT 35% VET <10G VERZ ZZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT BECEL PRO-ACTIV CALORIE LIGHT", "NEVO,VET/OLIE/SAUS,HALVARINEPRODUCT BECEL PRO-ACTIV LIGHT", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,MARGARINEPRODUCT 60% VET <17 G VERZ VETZ ONGEZ", "NEVO,VET/OLIE/SAUS,MARGARINEPRODUCT 60% VET <17 G VERZ ZZ", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,FRITUURVET VAST >24 G VERZ VETZ <10 G TRANSVETZ", "NEVO,VET/OLIE/SAUS,FRITUURVET >24 G VERZ VETZ <10 G TRANSVET", 1)
    name = name.replace("NEVO,VET/OLIE/SAUS,BAK/BRAADVET VAST 97% VET > 17G VERZ VETZ ONGEZ.", "NEVO,VET/OLIE/SAUS,BAK/BRAADVET VAST 97% VET > 17G VERZ", 1)


    if len(name) > 60: 
        print "X", len(name), name
        raise "Too long!"

#    print "T", name_orig, "!", name

    s += name + "^"
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

                    total = 0.01 * perc * float(r["nut"]["03002"])

                if total != 0.0:
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")

            elif t[1] == "6": # Simple addition
                calc = t[3:].split("+")
                
                # TODO What if something is not available?
                perc = 0.0
                for c in calc:
                    if r["nut"].has_key(c): perc += float(r["nut"][c])

                if perc != 0.0: 
                    total = 0.01 * perc * float(r["nut"]["03002"])
                    s += ("%.3f" % (total)).rstrip("0").rstrip(".")



        elif r["nut"].has_key(t):
            if float(r["nut"][t]) == 0.0:
                pass
            else:
                if nutrient_list[t]["unit"] == "%":
                    raise "Must do this explicit!"
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



