# Convert NEVO to ASDA nutrition format.
# -*- coding: iso-8859-15 -*-


# Food id 50000+
# food group 5000+

nutrient_list = {}

f = open("../Nevo/Nevo-Nutrienten_Lijst_Online versie 2011_3.0.txt")

for l in f.readlines():
    code = l[0:5]
    name = l[7:37].rstrip()
    meeteenheid = l[39:44].rstrip()
    english_name = l[49:80].rstrip()        # Thrown away.

    nutrient_list[code] = {"name": name, "unit": meeteenheid }

f.close()


conversion_table = []

f = open("nut.txt")
fdef = open("NUTR_DEF.txt") # To verify units are the same.

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

f = open("../Nevo/Nevo-Online versie 2011_3.0.dat")
#f = open("/tmp/30.dat")

l = f.readline().strip()
header = False


def printFoodRecord(r):

    # Use empty range from sr25.nut (50000 - 60000)
    s = ""
    s += repr(int(r["Productcode"])+50000) + "^"
    s += r["Productgroepcode"] + "^"

    # Alway add NEVO, to make it easier to know what is dutch
    name = ""
#    if len(r["Fabrikantnaam"]) != 0:
#        name += r["Fabrikantnaam"].upper() + ","
    name += r["Product_omschrijving"]

    name_orig = name

    # Replace some names.
    name = name.replace("ë", "e", 1)


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


    sql = "INSERT INTO food_des (NDB_No, FdGrp_Cd, Long_Desc, Shrt_Desc, Refuse, PROCNT, FAT, CHOCDF, ASH, ENERC_KCAL, STARCH, SUCS, GLUS, FRUS, LACS, MALS, ALC, WATER, ADPROT, CAFFN, THEBRN, ENERC_KJ, SUGAR, GALS, FIBTG, CA, FE, MG, P, K, NA, ZN, CU, FLD, MN, SE, VITA_IU, RETOL, VITA_RAE, CARTB, CARTA, TOCPHA, VITD, ERGCAL, CHOCAL, VITD_BOTH, CRYPX, LYCPN, LUT_ZEA, TOCPHB, TOCPHG, TOCPHD, VITC, THIA, RIBF, NIA, PANTAC, VITB6A, FOL, VITB12, CHOLN, MK4, VITK1D, VITK1, FOLAC, FOLFD, FOLDFE, BETN, TRP_G, THR_G, ILE_G, LEU_G, LYS_G, MET_G, CYS_G, PHE_G, TYR_G, VAL_G, ARG_G, HISTN_G, ALA_G, ASP_G, GLU_G, GLY_G, PRO_G, SER_G, HYP, VITE_ADDED, VITB12_ADDED, CHOLE, FATRN, FASAT, F4D0, F6D0, F8D0, F10D0, F12D0, F14D0, F16D0, F18D0, F20D0, F18D1, F18D2, F18D3, F20D4, F22D6, F22D0, F14D1, F16D1, F18D4, F20D1, F20D5, F22D1, F22D5, PHYSTR, STID7, CAMD5, SITSTR, FAMS, FAPU, F15D0, F17D0, F24D0, F16D1T, F18D1T, F22D1T, F18D2T, F18D2I, F18D2TT, F18D2CLA, F24D1C, F20D2CN6, F16D1C, F18D1C, F18D2CN6, F22D1C, F18D3CN6, F17D1, F20D3, FATRNM, FATRNP, F13D0, F15D1, F18D3CN3, F20D3N3, F20D3N6, F20D4N6, F18D3I, F21D5, F22D4, F18D1TN7)"
    sql += " VALUES ("

    fields = s.split("^")
    sql += fields[0] + ","
    sql += repr(int(fields[1])+5000) + ","
    sql += "\""+fields[2]+"\"" + ","
    sql += "\""+fields[2]+"\"" + ","

    if len(fields[4]) == 0: sql += "NULL,"
    else: sql += fields[4] + ","
    for i in range(8, 146+8):
        if fields[i] == "-0": sql += "NULL,"
        elif fields[i] == "": sql += "0,"
        else: sql += fields[i] + ","
            
    sql = sql.rstrip(",") + ")"
    print sql

    sql = "INSERT INTO weight( NDB_No, Seq, Amount, Msre_Desc, whectograms, origSeq, origAmount, orighectograms) VALUES ("
    sql += fields[0] + ","
    sql += "99,100.0,\"grams\",1.0,99,100.0,1.0)"
    print sql


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



