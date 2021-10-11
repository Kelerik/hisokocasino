import configparser

config = configparser.ConfigParser()
config.read("data/config.ini")


def loadconfigint(variablename):
    try:
        v = config["config"][variablename]
    except KeyError:
        v = input("ERROR: '" + variablename + "' not found in config. Run config and save new data.")
        print(v)
        exit()
    if v.isdigit():
        return int(v)
    else:
        v = input("ERROR: Check '" + variablename + "' in config. Must be a whole number.")
        print(v)
        exit()


def loadconfigfloat(variablename):
    try:
        v = config["config"][variablename]
    except KeyError:
        v = input("ERROR: '" + variablename + "' not found in config. Run config and save new data.")
        print(v)
        exit()
    if v.replace('.', '', 1).isdigit() and "." in v:
        return float(v)
    else:
        v = input("ERROR: Check '" + variablename + "' in config. Must be a decimal number.")
        print(v)
        exit()


activetime = loadconfigint("activetime")
chatminimum = loadconfigint("chatminimum")
paytimer = loadconfigint("paytimer")
goldpayout = loadconfigint("goldpayout")
raregoldpayout = loadconfigint("raregoldpayout")
goldconvert = loadconfigint("goldconvert")
raregoldconvert = loadconfigint("raregoldconvert")
givecooldown = loadconfigint("givecooldown")
startergold = loadconfigint("startergold")

subdaily = loadconfigint("subdaily")
subpay1 = loadconfigint("subpay1")
subpay2 = loadconfigint("subpay2")
subpay3 = loadconfigint("subpay3")

slotscooldown = loadconfigint("slotscooldown")
slotsodds = loadconfigint("slotsodds") / 100
kapowchance = loadconfigint("kapowchance") / 100
kapowpenalty = loadconfigfloat("kapowpenalty")
catebonus = loadconfigint("catebonus") / 100
slotsfaces = config["config"]["slotsfaces"].split(" ")

bjinterval = loadconfigint("bjinterval")
bjtimeout = loadconfigint("bjtimeout")
bjpayout = loadconfigfloat("bjpayout")

senpaicost = loadconfigint("senpaicost")
senpaiodds = loadconfigint("senpaiodds")
senpaigold = loadconfigint("senpaigold")
senpairaregold = loadconfigint("senpairaregold")

titlecost = loadconfigint("titlecost")
titleodds = loadconfigint("titleodds")
titlecooldown = loadconfigint("titlecooldown")
titlespay = config["config"]["titlespay"]

petcost = loadconfigint("petcost")
petodds = loadconfigint("petodds")
petcooldown = loadconfigint("petcooldown")
petlevelcooldown = loadconfigint("petlevelcooldown")

raidtimermin = loadconfigint("raidtimermin") * 60
raidtimermax = loadconfigint("raidtimermax") * 60
raidstealignore = loadconfigfloat("raidstealignore") / 100
raidstealwipe = loadconfigfloat("raidstealwipe") / 100

rouletteinterval = loadconfigint("rouletteinterval")

lotterycost = loadconfigint("lotterycost")
lotteryodds = loadconfigint("lotteryodds")
lotteryprize = loadconfigint("lotteryprize")