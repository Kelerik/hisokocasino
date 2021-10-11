from tkinter import *
from tkinter import ttk, scrolledtext, messagebox
import configparser


def verifyfloat(number, variablename):
    if not (number.replace(".", "", 1).isdigit() and "." in number):
        errorlist.append("'" + variablename + "' must be a decimal number")


def verifyinteger(number, variablename):
    if not number.isdigit():
        errorlist.append("'" + variablename + "' must be a whole number")


def makeform(tab, text1, text2, row):
    Label(tab, text=text1 + " :").grid(row=row, column=0, sticky="NW", pady=2, padx=4)
    if text2 is not None:
        Label(tab, text=text2).grid(row=row, column=2, sticky="NW")


def savechanges():
    # tab 1
    verifyinteger(e_activetime.get(), "Activity timer")
    verifyinteger(e_chatminimum.get(), "Minimum chatters required")
    verifyinteger(e_paytimer.get(), "Pay timer")
    verifyinteger(e_goldpayout.get(), "Gold paid")
    verifyinteger(e_raregoldpayout.get(), "Raregold paid")
    verifyinteger(e_givecooldown.get(), "Cooldown for giving raregold")
    verifyinteger(e_goldconvert.get(), "Conversion from")
    verifyinteger(e_raregoldconvert.get(), "Conversion to")
    verifyinteger(e_startergold.get(), "Starter gold")
    # tab 2
    verifyinteger(e_slotscooldown.get(), "Slots cooldown")
    verifyfloat(e_kapowpenalty.get(), "Kapow penalty")
    verifyinteger(e_catebonus.get(), "Cate bonus")
    # tab 3
    verifyinteger(e_bjinterval.get(), "Blackjack time interval")
    verifyinteger(e_bjtimeout.get(), "Time limit for making choices")
    verifyfloat(e_bjpayout.get(), "Blackjack multiplier")
    # tab 4
    verifyinteger(e_senpaicost.get(), "Senpai cost")
    verifyinteger(e_senpaiodds.get(), "Senpai odds")
    verifyinteger(e_senpaigold.get(), "Senpai gold payment")
    verifyinteger(e_senpairaregold.get(), "Senpai raregold payment")
    # tab 5
    verifyinteger(e_titlecost.get(), "Title cost")
    verifyinteger(e_titleodds.get(), "Title odds")
    verifyinteger(e_titlecooldown.get(), "Title cooldown")
    # tab 6
    verifyinteger(e_petcost.get(), "Pet cost")
    verifyinteger(e_petodds.get(), "Pet odds")
    verifyinteger(e_petcooldown.get(), "Pet cooldown")
    verifyinteger(e_petlevelcooldown.get(), "Pet levelup cooldown")
    # tab 7
    verifyinteger(e_subdaily.get(), "Daily pay")
    verifyinteger(e_subpay1.get(), "Tier 1 pay")
    verifyinteger(e_subpay2.get(), "Tier 2 pay")
    verifyinteger(e_subpay3.get(), "Tier 3 pay")
    # tab 8
    verifyinteger(e_raidtimermin.get(), "Raid timer min")
    verifyinteger(e_raidtimermax.get(), "Raid timer max")
    verifyfloat(e_raidstealignore.get(), "Raid steal ignore")
    verifyfloat(e_raidstealwipe.get(), "Raid steal wipe")
    # tab 9
    verifyinteger(e_rouletteinterval.get(), "Roulette time interval")
    # tab 10
    verifyinteger(e_lotterycost.get(), "Lottery entry cost")
    verifyinteger(e_lotteryodds.get(), "Lottery odds")
    verifyinteger(e_lotteryprize.get(), "Lottery prize")

    # check errors
    global errorlist
    if len(errorlist) > 0:
        messagebox.showwarning(str(len(errorlist)) + " error(s)", "\n".join(errorlist))
        errorlist = []

    # else no errors, finally save data
    else:
        # tab 1
        config.set("config", "activetime", str(e_activetime.get()))
        config.set("config", "chatminimum", str(e_chatminimum.get()))
        config.set("config", "paytimer", str(e_paytimer.get()))
        config.set("config", "goldpayout", str(e_goldpayout.get()))
        config.set("config", "raregoldpayout", str(e_raregoldpayout.get()))
        config.set("config", "givecooldown", str(e_givecooldown.get()))
        config.set("config", "goldconvert", str(e_goldconvert.get()))
        config.set("config", "raregoldconvert", str(e_raregoldconvert.get()))
        config.set("config", "subdaily", str(e_subdaily.get()))
        config.set("config", "startergold", str(e_startergold.get()))
        # tab 2
        config.set("config", "slotsfaces", str(e_slotsfaces.get("1.0", "end-1c")))
        config.set("config", "slotscooldown", str(e_slotscooldown.get()))
        config.set("config", "kapowpenalty", str(e_kapowpenalty.get()))
        config.set("config", "catebonus", str(e_catebonus.get()))
        config.set("config", "slotsodds", str(e_slotsodds.get()))
        config.set("config", "kapowchance", str(e_kapowchance.get()))
        # tab 3
        config.set("config", "bjinterval", str(e_bjinterval.get()))
        config.set("config", "bjtimeout", str(e_bjtimeout.get()))
        config.set("config", "bjpayout", str(e_bjpayout.get()))
        # tab 4
        config.set("config", "senpaicost", str(e_senpaicost.get()))
        config.set("config", "senpaiodds", str(e_senpaiodds.get()))
        config.set("config", "senpaigold", str(e_senpaigold.get()))
        config.set("config", "senpairaregold", str(e_senpairaregold.get()))
        # tab 5
        config.set("config", "titlecost", str(e_titlecost.get()))
        config.set("config", "titleodds", str(e_titleodds.get()))
        config.set("config", "titlecooldown", str(e_titlecooldown.get()))
        config.set("config", "titlespay", str(e_titlespay.get("1.0", "end-1c")).lower())
        # tab 6
        config.set("config", "petcost", str(e_petcost.get()))
        config.set("config", "petodds", str(e_petodds.get()))
        config.set("config", "petcooldown", str(e_petcooldown.get()))
        config.set("config", "petlevelcooldown", str(e_petlevelcooldown.get()))
        # tab 7
        config.set("config", "subdaily", str(e_subdaily.get()))
        config.set("config", "subpay1", str(e_subpay1.get()))
        config.set("config", "subpay2", str(e_subpay2.get()))
        config.set("config", "subpay3", str(e_subpay3.get()))
        # tab 8
        config.set("config", "raidtimermin", str(e_raidtimermin.get()))
        config.set("config", "raidtimermax", str(e_raidtimermax.get()))
        config.set("config", "raidstealignore", str(e_raidstealignore.get()))
        config.set("config", "raidstealwipe", str(e_raidstealwipe.get()))
        # tab 9
        config.set("config", "rouletteinterval", str(e_rouletteinterval.get()))
        # tab 10
        config.set("config", "lotterycost", str(e_lotterycost.get()))
        config.set("config", "lotteryodds", str(e_lotteryodds.get()))
        config.set("config", "lotteryprize", str(e_lotteryprize.get()))

        with open("data/config.ini", "w") as configfile:
            config.write(configfile)
        messagebox.showinfo("hisoChamp", "Changes saved.")
        main.quit()


def cancelconfig():
    if messagebox.askyesno("hisoCate", "Exit without saving changes?"):
        main.quit()


config = configparser.ConfigParser()
config.read("data/config.ini")

# load vars
# tab 1
activetime = config.get("config", "activetime", fallback="600")
chatminimum = config.get("config", "chatminimum", fallback="3")
paytimer = config.get("config", "paytimer", fallback="60")
goldpayout = config.get("config", "goldpayout", fallback="10")
raregoldpayout = config.get("config", "raregoldpayout", fallback="10")
givecooldown = config.get("config", "givecooldown", fallback="10")
goldconvert = config.get("config", "goldconvert", fallback="100")
raregoldconvert = config.get("config", "raregoldconvert", fallback="39")
startergold = config.get("config", "startergold", fallback="1000")
# tab 2
slotsfaces = config.get("config", "slotsfaces", fallback="")
slotscooldown = config.get("config", "slotscooldown", fallback="60")
kapowpenalty = config.get("config", "kapowpenalty", fallback="1.0")
catebonus = config.get("config", "catebonus", fallback="10")
slotsodds = config.get("config", "slotsodds", fallback="39")
kapowchance = config.get("config", "kapowchance", fallback="10")
# tab 3
bjinterval = config.get("config", "bjinterval", fallback="10")
bjtimeout = config.get("config", "bjtimeout", fallback="16")
bjpayout = config.get("config", "bjpayout", fallback="1.5")
# tab 4
senpaicost = config.get("config", "senpaicost", fallback="1000")
senpaiodds = config.get("config", "senpaiodds", fallback="1000")
senpaigold = config.get("config", "senpaigold", fallback="1000")
senpairaregold = config.get("config", "senpairaregold", fallback="1000")
# tab 5
titlecost = config.get("config", "titlecost", fallback="1000")
titleodds = config.get("config", "titleodds", fallback="500")
titlecooldown = config.get("config", "titlecooldown", fallback="600")
titlespay = config.get("config", "titlespay", fallback="miku=1000 rin=3400")
# tab 6
petcost = config.get("config", "petcost", fallback="1000")
petodds = config.get("config", "petodds", fallback="1000")
petcooldown = config.get("config", "petcooldown", fallback="600")
petlevelcooldown = config.get("config", "petlevelcooldown", fallback="39")
# tab 7
subdaily = config.get("config", "subdaily", fallback="1000")
subpay1 = config.get("config", "subpay1", fallback="5000")
subpay2 = config.get("config", "subpay2", fallback="10000")
subpay3 = config.get("config", "subpay3", fallback="25000")
# tab 8
raidtimermin = config.get("config", "raidtimermin", fallback="10")
raidtimermax = config.get("config", "raidtimermax", fallback="60")
raidstealignore = config.get("config", "raidstealignore", fallback="1.5")
raidstealwipe = config.get("config", "raidstealwipe", fallback="0.5")
# tab 9
rouletteinterval = config.get("config", "rouletteinterval", fallback="10")
# tab 10
lotterycost = config.get("config", "lotterycost", fallback="39")
lotteryodds = config.get("config", "lotteryodds", fallback="99999")
lotteryprize = config.get("config", "lotteryprize", fallback="1000000")

errorlist = []

main = Tk()
main.title('hisokocasino config')
main.geometry(("+%d+%d" % (main.winfo_screenwidth() / 3, main.winfo_screenheight() / 3)))

# Defines and places the notebook widget
nb = ttk.Notebook(main)
nb.grid(row=1, column=0, columnspan=49, rowspan=49, sticky='N')

# tab s
tab1 = ttk.Frame(nb)
nb.add(tab1, text="Pay")

tab2 = ttk.Frame(nb)
nb.add(tab2, text="Slots")

tab3 = ttk.Frame(nb)
nb.add(tab3, text="Blackjack")

tab4 = ttk.Frame(nb)
nb.add(tab4, text="Senpai")

tab5 = ttk.Frame(nb)
nb.add(tab5, text="Titles")

tab6 = ttk.Frame(nb)
nb.add(tab6, text="Pets")

tab7 = ttk.Frame(nb)
nb.add(tab7, text="Subscriber")

tab8 = ttk.Frame(nb)
nb.add(tab8, text="Raids")

tab9 = ttk.Frame(nb)
nb.add(tab9, text="Roulette")

tab10 = ttk.Frame(nb)
nb.add(tab10, text="Lottery")

btnsave = Button(main, text="Save", command=savechanges).grid(row=1, column=50, sticky="NWE", pady=10, padx=10)
btncancel = Button(main, text="Cancel", command=cancelconfig).grid(row=2, column=50, sticky="NWE", padx=10)

# tab 1
makeform(tab1, "Activity timer", "seconds", 0)
makeform(tab1, "Minimum chatters required", "chatters", 1)
makeform(tab1, "Pay timer", "seconds", 2)
makeform(tab1, "Gold paid", "gold", 3)
makeform(tab1, "Raregold paid", "raregold", 4)
makeform(tab1, "Cooldown for giving raregold", "seconds", 5)
makeform(tab1, "Conversion from", "gold", 6)
makeform(tab1, "Conversion to", "raregold", 7)
makeform(tab1, "Starter gold", "gold", 8)

e_activetime = Entry(tab1, width=10, justify="right")
e_chatminimum = Entry(tab1, width=10, justify="right")
e_paytimer = Entry(tab1, width=10, justify="right")
e_goldpayout = Entry(tab1, width=10, justify="right")
e_raregoldpayout = Entry(tab1, width=10, justify="right")
e_givecooldown = Entry(tab1, width=10, justify="right")
e_goldconvert = Entry(tab1, width=10, justify="right")
e_raregoldconvert = Entry(tab1, width=10, justify="right")
e_startergold = Entry(tab1, width=10, justify="right")

e_activetime.grid(row=0, column=1)
e_chatminimum.grid(row=1, column=1)
e_paytimer.grid(row=2, column=1)
e_goldpayout.grid(row=3, column=1)
e_raregoldpayout.grid(row=4, column=1)
e_givecooldown.grid(row=5, column=1)
e_goldconvert.grid(row=6, column=1)
e_raregoldconvert.grid(row=7, column=1)
e_startergold.grid(row=8, column=1)

e_activetime.insert(0, activetime)
e_chatminimum.insert(0, chatminimum)
e_paytimer.insert(0, paytimer)
e_goldpayout.insert(0, goldpayout)
e_raregoldpayout.insert(0, raregoldpayout)
e_givecooldown.insert(0, givecooldown)
e_goldconvert.insert(0, goldconvert)
e_raregoldconvert.insert(0, raregoldconvert)
e_startergold.insert(0, startergold)

# tab 2
makeform(tab2, "Faces", None, 0)
makeform(tab2, "Cooldown", "seconds", 1)
makeform(tab2, "Kapow penalty", "multiplier", 2)
makeform(tab2, "Cate bonus", "%", 3)
makeform(tab2, "Odds of match (%)", None, 4)
makeform(tab2, "Odds of Kapow (%)", None, 5)

e_slotsfaces = scrolledtext.ScrolledText(tab2, width=10, height=6, wrap=WORD)
e_slotscooldown = Entry(tab2, width=10, justify="right")
e_kapowpenalty = Entry(tab2, width=10, justify="right")
e_catebonus = Entry(tab2, width=10, justify="right")
e_slotsodds = Scale(tab2, width=6, length=200, from_=1, to=50, orient=HORIZONTAL)
e_kapowchance = Scale(tab2, width=6, from_=1, to=50, orient=HORIZONTAL)

e_slotsfaces.grid(row=0, column=1, columnspan=2, sticky="WE")
e_slotscooldown.grid(row=1, column=1)
e_kapowpenalty.grid(row=2, column=1)
e_catebonus.grid(row=3, column=1)
e_slotsodds.grid(row=4, column=1, columnspan=2, sticky="WE")
e_kapowchance.grid(row=5, column=1, columnspan=2, sticky="WE")

e_slotsfaces.insert(INSERT, slotsfaces)
e_slotscooldown.insert(0, slotscooldown)
e_kapowpenalty.insert(0, kapowpenalty)
e_catebonus.insert(0, catebonus)
e_slotsodds.set(int(slotsodds))
e_kapowchance.set(int(kapowchance))

# tab 3
makeform(tab3, "Blackjack time interval", "minutes", 0)
makeform(tab3, "Time limit for making choices", "seconds", 1)
makeform(tab3, "Blackjack payout", "multiplier", 2)

e_bjinterval = Entry(tab3, width=10, justify="right")
e_bjtimeout = Entry(tab3, width=10, justify="right")
e_bjpayout = Entry(tab3, width=10, justify="right")

e_bjinterval.grid(row=0, column=1)
e_bjtimeout.grid(row=1, column=1)
e_bjpayout.grid(row=2, column=1)

e_bjinterval.insert(0, bjinterval)
e_bjtimeout.insert(0, bjtimeout)
e_bjpayout.insert(0, bjpayout)

# tab 4
makeform(tab4, "Cost to roll", "gold", 0)
makeform(tab4, "Odds of winning", "1/x", 1)
makeform(tab4, "Senpai payment", "gold", 2)
makeform(tab4, "Senpai payment", "raregold", 3)

e_senpaicost = Entry(tab4, width=10, justify="right")
e_senpaiodds = Entry(tab4, width=10, justify="right")
e_senpaigold = Entry(tab4, width=10, justify="right")
e_senpairaregold = Entry(tab4, width=10, justify="right")

e_senpaicost.grid(row=0, column=1)
e_senpaiodds.grid(row=1, column=1)
e_senpaigold.grid(row=2, column=1)
e_senpairaregold.grid(row=3, column=1)

e_senpaicost.insert(0, senpaicost)
e_senpaiodds.insert(0, senpaiodds)
e_senpaigold.insert(0, senpaigold)
e_senpairaregold.insert(0, senpairaregold)

# tab 5
makeform(tab5, "Cost to roll", "gold", 0)
makeform(tab5, "Odds of winning", "1/x", 1)
makeform(tab5, "Cooldown", "seconds", 2)
makeform(tab5, "Titles/pay", None, 3)

e_titlecost = Entry(tab5, width=10, justify="right")
e_titleodds = Entry(tab5, width=10, justify="right")
e_titlecooldown = Entry(tab5, width=10, justify="right")
e_titlespay = scrolledtext.ScrolledText(tab5, width=20, height=10, wrap=WORD)

e_titlecost.grid(row=0, column=1)
e_titleodds.grid(row=1, column=1)
e_titlecooldown.grid(row=2, column=1)
e_titlespay.grid(row=3, column=1, columnspan=2, sticky="WE")

e_titlecost.insert(0, titlecost)
e_titleodds.insert(0, titleodds)
e_titlecooldown.insert(0, titlecooldown)
e_titlespay.insert(INSERT, titlespay)

# tab 6
makeform(tab6, "Cost to roll", "gold", 0)
makeform(tab6, "Odds of winning", "1/x", 1)
makeform(tab6, "Cooldown", "seconds", 2)
makeform(tab6, "Levelup cooldown", "minutes", 3)

e_petcost = Entry(tab6, width=10, justify="right")
e_petodds = Entry(tab6, width=10, justify="right")
e_petcooldown = Entry(tab6, width=10, justify="right")
e_petlevelcooldown = Entry(tab6, width=10, justify="right")

e_petcost.grid(row=0, column=1)
e_petodds.grid(row=1, column=1)
e_petcooldown.grid(row=2, column=1)
e_petlevelcooldown.grid(row=3, column=1)

e_petcost.insert(0, petcost)
e_petodds.insert(0, petodds)
e_petcooldown.insert(0, petcooldown)
e_petlevelcooldown.insert(0, petlevelcooldown)

# tab 7
makeform(tab7, "Daily pay", "gold", 0)
makeform(tab7, "Tier 1 pay", "gold", 1)
makeform(tab7, "Tier 2 pay", "gold", 2)
makeform(tab7, "Tier 3 pay", "gold", 3)

e_subdaily = Entry(tab7, width=10, justify="right")
e_subpay1 = Entry(tab7, width=10, justify="right")
e_subpay2 = Entry(tab7, width=10, justify="right")
e_subpay3 = Entry(tab7, width=10, justify="right")

e_subdaily.grid(row=0, column=1)
e_subpay1.grid(row=1, column=1)
e_subpay2.grid(row=2, column=1)
e_subpay3.grid(row=3, column=1)

e_subdaily.insert(0, subdaily)
e_subpay1.insert(0, subpay1)
e_subpay2.insert(0, subpay2)
e_subpay3.insert(0, subpay3)

# tab 8
makeform(tab8, "Raid time interval (min)", "minutes", 0)
makeform(tab8, "Raid time interval (max)", "minutes", 1)
makeform(tab8, "Raregold steal (ignored)", "%", 2)
makeform(tab8, "Raregold steal (wipe)", "%", 3)

e_raidtimermin = Entry(tab8, width=10, justify="right")
e_raidtimermax = Entry(tab8, width=10, justify="right")
e_raidstealignore = Entry(tab8, width=10, justify="right")
e_raidstealwipe = Entry(tab8, width=10, justify="right")

e_raidtimermin.grid(row=0, column=1)
e_raidtimermax.grid(row=1, column=1)
e_raidstealignore.grid(row=2, column=1)
e_raidstealwipe.grid(row=3, column=1)

e_raidtimermin.insert(0, raidtimermin)
e_raidtimermax.insert(0, raidtimermax)
e_raidstealignore.insert(0, raidstealignore)
e_raidstealwipe.insert(0, raidstealwipe)

# tab 9
makeform(tab9, "Roulette time interval", "minutes", 0)

e_rouletteinterval = Entry(tab9, width=10, justify="right")

e_rouletteinterval.grid(row=0, column=1)

e_rouletteinterval.insert(0, rouletteinterval)

# tab 10
makeform(tab10, "Lottery entry cost", "gold", 0)
makeform(tab10, "Lottery odds", "1/x", 1)
makeform(tab10, "Lottery prize", "gold", 2)

e_lotterycost = Entry(tab10, width=10, justify="right")
e_lotteryodds = Entry(tab10, width=10, justify="right")
e_lotteryprize = Entry(tab10, width=10, justify="right")

e_lotterycost.grid(row=0, column=1)
e_lotteryodds.grid(row=1, column=1)
e_lotteryprize.grid(row=2, column=1)

e_lotterycost.insert(0, lotterycost)
e_lotteryodds.insert(0, lotteryodds)
e_lotteryprize.insert(0, lotteryprize)

# start
main.mainloop()
