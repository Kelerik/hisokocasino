import json
import re
import socket
import threading
from collections import deque
from math import log10
from os import path
from textwrap import wrap
from time import time, strftime, sleep, localtime
from emoji import emojize
from random import Random
from bj import *
from configloader import *
from hisoCate import *
from slots import *
from weather import getweather

s = socket.socket()
irc_nick = "hisokocasino"
irc_chan = "hisokeee"
casinoversion = "Version 6.11, Updated Jul 20 2020"

stayalive = True
threadsenable = True
slotsenable = False
nochat = False

if path.isfile("offlinemode.txt"):
    offlinemode = True
else:
    offlinemode = False

offlineusername = irc_nick

bjenable = False
bjopen = False
bjdesignate = None
bjplayers = {}
bjdeal = None
bjactive = False
seqtime = 4
bjtimer = time() * 2
bjqueue = deque([""])
bjdealerturns = deque([None])

gambleactive = False
gambleopen = False
gamblemin = 0
gamblemax = 0
gamblemultiply = 1
gamblepay = 0
gambleplayers = {}
gamblechoices = {}

raffleactive = False
raffleplayers = []
rafflewinlist = []
raffleprize = 0
rafflecurrency = None
rafflecurrencystr = ""
rafflekeyword = ""
rafflewinmsg = ""

hiloopen = False
hiloactive = False
hilouser = ""
hilorounds = []
hilobet = 0
hilocard = 0
hilosuit = 0
hilocurrency = None
hilocurrencystr = ""

username = ""
message = ""
activechat = {}
msginque = deque([])
msgoutque = deque([])
pyramidcache = ["", ""]
pingtimer = time() + 360
renameconfirmation = ""
casino = 0
commandtimer = 0
commandcooldown = 8
msglengthlimit = 500
giftsubtimer = 0
giftsubqueue = {}
hitmancost = 10000
casinomute = False

raidenable = False
raidactive = False
raidopen = False
raidplayers = []
raidtimer = 0
raidlevel = 0
raidboss = ""
raidmsgque = deque([])

rouletteenable = False
rouletteactive = False
rouletteopen = False
rouletteplayers = {}
roulettetimer = 0
rlmsgque = deque([])
roulettemin = 0
roulettemax = 0

bancasino = {}
bangiveraregold = {}
bantitle = {}
banpet = {}
banpetlevel = {}
banlottery = {}

# === chat REs ===
# https://dev.twitch.tv/docs/irc/tags/

# > @badges=global_mod/1,turbo/1;color=#0D4200;display-name=dallas;emotes=25:0-4,12-16/1902:6-10;id=b34ccfc7-4977-403a-8a94-33c6bac34fb8;mod=0;room-id=1337;
# subscriber=0;tmi-sent-ts=1507246572675;turbo=1;user-id=1337;user-type=global_mod :ronni!ronni@ronni.tmi.twitch.tv PRIVMSG #dallas :Kappa Keepo Kappa
re_chat = re.compile(r"^@(\S+) :(\w+)!\w+@\w+\.tmi\.twitch\.tv (PRIVMSG|WHISPER) #?\w+ :(.+)")

# > @badges=<badges>;color=<color>;display-name=<display-name>;emotes=<emotes>;id=<id-of-msg>;login=<user>;mod=<mod>;msg-id=<msg-id>;
# room-id=<room-id>;subscriber=<subscriber>;system-msg=<system-msg>;tmi-sent-ts=<timestamp>;turbo=<turbo>;user-id=<user-id>;
# user-type=<user-type> :tmi.twitch.tv USERNOTICE #<channel> :<message>
re_usernotice = re.compile(r"^(\S+) :tmi\.twitch\.tv USERNOTICE #?\w+ :(.+)")


# return data loaded from a file. if error occurs, use fallback if there is one
def loadjsondata(filename, fallback=None):
    try:
        with open("data/" + filename, encoding="utf-8") as j:
            loadedf = json.load(j)
    except:
        if fallback is None:
            a = input("Error loading " + filename)
            print(a)
            global stayalive
            stayalive = False
            return
        else:
            a = input("Error loading " + filename + ". Hit Enter to create a new blank file and start from scratch.")
            print(a)
            return fallback

    return loadedf


irc_pass = loadjsondata("oauth.txt")
gold = loadjsondata("gold.txt", {})
raregold = loadjsondata("raregold.txt", {})
slotsstats = loadjsondata("slotsstats.txt", {})
bjstats = loadjsondata("bjstats.txt", {})
roulettestats = loadjsondata("roulettestats.txt", {})
masterlist = loadjsondata("masterlist.txt", [])
senpais = loadjsondata("senpais.txt", {})
vocaloids = loadjsondata("vocaloids.txt", {})
dailies = loadjsondata("dailies.txt", {})
pets = loadjsondata("pets.txt", {})
emotestats = loadjsondata("emotestats.txt", {})


# connect to server
def serverconnect():
    try:
        s.connect(("irc.chat.twitch.tv", 6667))
        serversend("PASS " + irc_pass)
        serversend("NICK " + irc_nick)
        serversend("JOIN #" + irc_chan)
        serversend("CAP REQ :twitch.tv/commands")
        serversend("CAP REQ :twitch.tv/tags")
    except socket.gaierror:
        console("No internet connection. Trying again in 10 sec.")
        sleep(10)
        restart()


# restart the program
def restart():
    from os import execl
    from sys import executable, argv
    execl(executable, executable, *argv)


# send a message to the server directly
def serversend(msg):
    s.send((msg + "\r\n").encode("utf-8"))


# add a chat messsage to the queue, to be sent out by the outgoing message thread
def chat(msg):
    if casinomute is False or ismaster():
        global msgoutque
        # if message too long, split into multiple messages
        msgsplit = wrap(msg, width=msglengthlimit)
        msgoutque.extend(msgsplit)


# chat command with priority
def chatp(msg):
    global msgoutque
    msgoutque.appendleft(msg)


# returns a user's displayname, which is stored in the active users dictionary
def dname(user=None, senpaititle=True):
    if user is None:
        user = username
    if user in activechat:
        if activechat[user][1] == "":
            returnname = user
        else:
            returnname = activechat[user][1]
    else:
        returnname = user
    if issenpai(user) and senpaititle is True:
        returnname += " senpai"
    return returnname


# print to the console. non-ascii characters removed
def console(msg):
    print("[" + strftime("%H:%M:%S") + "] " + re.sub(r"[^\x00-\x7F]", "*", msg))


# regex search within the incoming chat message
def textmatch(msgtxt):
    if re.search(msgtxt, message):
        return True
    else:
        return False


# return a number converted to string, shortened with a suffix
def shortnum(number, signed=False):
    if number < 0:
        neg = True
        number = abs(number)
    else:
        neg = False
    # remember not to use log functions on zero or negative number
    if number >= 1e4:
        suffixlist = ["K", "M", "B", "T", " quadrillion", " quintillion", " sextillion", " septillion", " octillion", " nonillion", " decillion"]
        try:
            # different suffix for every 3 extra digits
            suffix = suffixlist[int(log10(number) / 3) - 1]
            number = round(number / (1000 ** int(log10(number) / 3)), 1)
        except IndexError:
            # if not enough suffix names added, use scientific notation
            suffix = "e" + str(int(log10(number)))
            number = round(number / (10 ** int(log10(number))), 1)
    else:
        suffix = ""
    if neg is True:
        number *= -1
    if signed is True:
        return "{:+}".format(number) + suffix
    else:
        return str(number) + suffix


# save a variable's data to a file
def jdump(filename, variable):
    with open("data/" + filename, 'w', encoding="utf-8") as v:
        json.dump(variable, v)


# save data to their respective files
def savedata():
    jdump("gold.txt", gold)
    jdump("raregold.txt", raregold)
    jdump("senpais.txt", senpais)
    jdump("vocaloids.txt", vocaloids)
    jdump("dailies.txt", dailies)
    jdump("pets.txt", pets)
    jdump("emotestats.txt", emotestats)


# add an amount to the specified currency's dictionary. if item doesn't exist, add it automatically. subtract using negative numbers.
def deal(dictionary, name, amount):
    amount = int(amount)
    if name in dictionary:
        dictionary[name] += amount
    else:
        dictionary[name] = amount


# add a cooldown to a user's action
def dictban(dictionary, user, seconds):
    # if user != irc_nick and user != irc_chan:
    dictionary[user] = time() + abs(seconds)
    # this list never gets cleaned, but that shouldn't be a problem (yet)


# convert seconds to hh:mm:ss
def hmstime(seconds):
    hmsmin, hmssec = divmod(seconds, 60)
    if hmsmin == 0:
        return "{}s".format(hmssec)
    elif hmsmin < 60:
        return "{}m{}s".format(hmsmin, hmssec)
    else:
        hmshour, hmsmin = divmod(hmsmin, 60)
        return "{}h{}m".format(hmshour, hmsmin)


# check if the user is still on cooldown in the specified cooldown dictionary
def nodictban(bandictionary, actionmessage):
    if (username in bandictionary) and (time() < bandictionary[username]):
        secondstogo = round(bandictionary[username] - time())
        chat("{} — You cannot {} again for {}.".format(dname(), actionmessage, hmstime(secondstogo)))
        return False
    else:
        return True


# check if the user has any gold. if not, return false and post a message
def hasgold(amount=0, diff=False):
    if username in gold and gold[username] >= amount:
        return True
    elif username in gold and 0 < gold[username] < amount:
        if diff is False:
            chat(dname() + " — You don't have enough gold (" + shortnum(gold[username]) + ")")
        else:
            chat(dname() + " — You don't have enough gold (" + shortnum(gold[username]) + "). You need " + shortnum(amount - gold[username]) + " more.")
        return False
    else:
        chat(dname() + " — You don't have any gold.")
        return False


# check if a user has any raregold. if not, return false and post a message
def hasraregold(amount=0, diff=False):
    if username in raregold and raregold[username] >= amount:
        return True
    elif username in raregold and 0 < raregold[username] < amount:
        if diff is False:
            chat(dname() + " — You don't have enough raregold (" + shortnum(raregold[username]) + ")")
        else:
            chat(dname() + " — You don't have enough raregold (" + shortnum(raregold[username]) + "). You need " + shortnum(
                amount - raregold[username]) + " more.")
        return False
    else:
        chat(dname() + " — You don't have any raregold.")
        return False


# check if a user has a pet. if not, return false and post a message
def haspet():
    if username in pets and pets[username][0] is True:
        return True
    else:
        chat(dname() + " — You do not have a pet.")
        return False


# analyze a string from chat message and find what number the user is saying. accepts suffixes and decimals
def getnum(numbparse):
    if "all" in numbparse:  # do NOT use "=="
        numb = raregold[username]
    else:
        numb = float(re.search(r"\d+\.?\d*", numbparse).group(0))
        if re.search(r"\d[kmbt]", numbparse):
            suffix = re.search(r"\d([kmbt])", numbparse).group(1)
            if suffix == "k":
                numb *= 1e3
            elif suffix == "m":
                numb *= 1e6
            elif suffix == "b":
                numb *= 1e9
            elif suffix == "t":
                numb *= 1e12
        elif re.search(r"\de\d", numbparse):
            expnumb = re.search(r"e(\d+)", numbparse).group(1)
            numb *= 10 ** int(expnumb)
    return int(numb)


# add data to the user's slots log and save it
def slotsstatslog(bet, code):
    bet = abs(bet)
    if username not in slotsstats:
        slotsstats[username] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    slotsstats[username][0] += 1
    # 0: total plays, 1: raregold won, 2: raregold lost, 3: KAPOWs, 4: loss,
    # 5: 2x, 6: 2x/2x, 7: 3x, 8: 3x/2x, 9: 4x, 10: 5x
    if code <= 0:
        slotsstats[username][2] += bet
        if code < 0:
            slotsstats[username][3] += 1
        elif code == 0:
            slotsstats[username][4] += 1
    else:
        slotsstats[username][1] += bet
        if code == 4:
            slotsstats[username][5] += 1
        elif code == 8:
            slotsstats[username][6] += 1
        elif code == 9:
            slotsstats[username][7] += 1
        elif code == 13:
            slotsstats[username][8] += 1
        elif code == 16:
            slotsstats[username][9] += 1
        elif code == 25:
            slotsstats[username][10] += 1
    jdump("slotsstats.txt", slotsstats)


# add data to the user's bj log. saving is done later
def bjstatslog(win, user, playerclass):
    bet = int(playerclass.bet)
    if user not in bjstats:
        bjstats[user] = [0, 0, 0, 0, 0, 0, 0, 0]
    bjstats[user][0] += 1
    # 0: total plays, 1: raregold won, 2: raregold lost, 3: wins, 4: losses, 5: ties, 6: busts, 7: BJs
    if win is True:
        bjstats[user][1] += bet
        bjstats[user][3] += 1
    elif win is None:
        bjstats[user][5] += 1
    elif win is False:
        bjstats[user][2] += bet
        bjstats[user][4] += 1

    if playerclass.bust is True:
        bjstats[user][6] += 1
    elif playerclass.blackjack is True:
        bjstats[user][7] += 1


# reset all parameters for the gamble feature
def gamblereset():
    global gambleactive, gambleopen, gamblemin, gamblemax, gamblemultiply, gamblepay, gambleplayers, gamblechoices
    gambleactive = False
    gambleopen = False
    gamblemin = 0
    gamblemax = 0
    gamblemultiply = 1
    gamblepay = 0
    gambleplayers = {}
    gamblechoices = {}


# reset all parameters for the bj feature
def bjreset():
    global bjdesignate, bjplayers, bjdeal, bjtimer, bjactive, bjqueue
    bjtimer = time() + bjinterval * 60
    bjqueue = deque([""])
    bjdesignate = None
    bjplayers = {}
    bjdeal = None
    bjactive = False


# return a message with info about the current active gamble
def gamblesummary():
    choiceslist = []
    for x in sorted(gamblechoices):
        choiceslist.append(x + ": " + str(gamblechoices[x]))
    if len(gambleplayers) == 1:
        pluralstr = " bet has"
    else:
        pluralstr = " bets have"
    output = str(len(gambleplayers)) + pluralstr + " been placed: [" + "], [".join(choiceslist) + "]."
    return output


# check if the user is a master
def ismaster(truemaster=False):
    if username == irc_chan or username == irc_nick or username == "kelerik":
        return True
    elif username in masterlist:
        if truemaster is False:
            return True
        else:
            return False
    else:
        return False


# calculate date difference
def deltatime(previoustime):
    deltaseconds = time() - previoustime
    deltaminutes = deltaseconds / 60
    deltahours = deltaminutes / 60
    deltadays = deltahours / 24
    deltayears = deltadays / 365.25
    if deltayears >= 1:
        output = [round(deltayears, 1), " year"]
    elif deltadays >= 1:
        output = [round(deltadays, 1), " day"]
    elif deltahours >= 1:
        output = [round(deltahours, 1), " hour"]
    elif deltaminutes >= 1:
        output = [int(deltaminutes), " minute"]
    else:
        output = [int(deltaseconds), " second"]
    if output[0] != 1:
        output[1] += "s"
    return str(output[0]) + output[1]


# senpai check
def issenpai(name):
    if name in senpais and senpais[name][0] is True:
        return True


# hilo reset
def hiloreset():
    global hiloactive, hilobet, hilorounds, hilouser, hiloopen, hilocard, hilocurrency, hilosuit, hilocurrencystr
    hiloopen = False
    hiloactive = False
    hilouser = ""
    hilorounds = []
    hilobet = 0
    hilocard = 0
    hilosuit = 0
    hilocurrency = None
    hilocurrencystr = ""


# vocaloid name check
def isvocaloid(name):
    if re.search(r"(^|\W)" + name + r"=\d+", titlespay):
        return True
    else:
        return False


# roll fail message
def rollfail(attempts):
    if attempts == 1:
        return choice(titlefail)
    elif attempts in logincrements:
        return "Congratulations! hisoChamp You failed for the " + str(attempts) + "th time! "
    else:
        return choice(titlefail) + ". " + choice(titleattempts).format(attempts)


# pay pet according to its level. no error if user has no pet
def paypetpercent(user, amount):
    if user in pets and pets[user][0] is True:
        # squre root function
        pets[user][4] += int(amount * (pets[user][3] * 0.001521) ** 0.5)


# pay pet directly. no error if user has no pet
def paypet(user, amount):
    if user in pets and pets[user][0] is True:
        pets[user][4] += int(amount)


# display user gold and difference
def golddiff(user, amount):
    return "[{} gold]({})".format(shortnum(gold[user]), shortnum(amount, signed=True))


# display user gold and difference
def raregolddiff(user, amount):
    return "[{} raregold]({})".format(shortnum(raregold[user]), shortnum(amount, signed=True))


# raid reset
def raidreset():
    global raidtimer, raidplayers, raidactive, raidopen, raidmsgque
    raidactive = False
    raidopen = False
    raidplayers = []
    raidmsgque = deque([])
    raidtimer = time() + SystemRandom().randint(raidtimermin, raidtimermax)


# roulette reset
def roulettereset():
    global roulettetimer, rouletteplayers, rouletteactive, rouletteopen, rlmsgque
    rouletteactive = False
    rouletteopen = False
    rouletteplayers = {}
    rlmsgque = deque([])
    roulettetimer = time() + rouletteinterval * 60


# roulette number with emoji colour
def roulettecolour(number):
    if number in red:
        return emojize(":red_circle: ") + str(number)
    elif number in black:
        return emojize(":black_circle: ") + str(number)
    elif number == 0:
        return emojize(":green_heart: ") + str(number)
    elif number == -1:
        return emojize(":green_heart: 00")


# roulette test add players
def roulettetest():
    rt = 0
    while rt <= 36:
        rouletteplayers[str(rt)] = [1, str(rt)]
        rt += 1
    for rtt in roulettebets:
        rouletteplayers[str(rtt)] = [1, str(rtt)]


# roulette log
def roulettestatslog(user, bet):
    # 0: plays, 1: gold won, 2:, gold lost, 3: wins, 4: losses
    if user not in roulettestats:
        roulettestats[user] = [0, 0, 0, 0, 0]
    roulettestats[user][0] += 1
    if bet > 0:
        roulettestats[user][1] += bet
        roulettestats[user][3] += 1
    else:
        roulettestats[user][2] -= bet
        roulettestats[user][4] += 1


# emote counting. not starting until 2020
def countemotes(messageserver, messageuser):
    currentyear = strftime("%Y")
    if int(currentyear) > 2019:
        if currentyear not in emotestats:
            emotestats[currentyear] = {}
        emoteindexes = re.search(r"emotes=([^;]*);", messageserver)
        if emoteindexes is not None:
            emoteannounced = False
            randomannounced = False
            # example of original string: "emotes=25:0-4,12-16/1902:6-10;"
            # example after modification: ["0-4", "12-16", "6-10"]
            emoteindexes = re.findall(r"(\d+-\d+)", emoteindexes.group(1))
            for emoteindex in emoteindexes:
                # change "0-4" to [0, 4]
                emoteindexnumbers = emoteindex.split("-")
                # index the message string to get the emote
                emotename = messageuser[int(emoteindexnumbers[0]):int(emoteindexnumbers[1]) + 1]
                # if hiso emote
                if re.search(r"^hiso", emotename) and "_" not in emotename:
                    # remove the "hiso" prefix
                    emotename = emotename.lstrip("hiso")
                    # count
                    if emotename not in emotestats[currentyear]:
                        emotestats[currentyear][emotename] = 0
                    emotestats[currentyear][emotename] += 1
                    # announce milestones. random chance cannnot occur more than once per message.
                    if (emotestats[currentyear][emotename] in logincrements or (rng(0.01) and (emoteannounced is randomannounced is False))) and nogames():
                        chat("{:,} {}s posted in {} hiso{}".format(emotestats[currentyear][emotename], emotename, currentyear, emotename))
                        emoteannounced = True
                    randomannounced = True


# time of next day
def nextday():
    return int(time() / 86400) * 86400 + 86400


# check if no games are running
def nogames():
    if raidactive is bjactive is rouletteactive is False:
        return True
    else:
        return False


# random chance
def rng(odds):
    if SystemRandom().random() < odds:
        return True
    else:
        return False


# --- Basic functions end ---


# --- Thread functions start ---

# BOT FUNCTIONS RESPONDING TO MESSAGES
def msgprocess(response):
    if not re.search("^:", response):
        console(response)
    if re_chat.search(response):
        global username, message
        global pyramidcache, commandtimer
        global slotsenable, casino, casinomute
        global bjenable, bjdesignate, bjplayers, bjdeal, bjtimer, bjactive, bjopen
        global gamblemax, gamblemin, gambleactive, gamblemultiply, gamblepay, gambleopen, gamblechoices
        global raffleactive, rafflecurrency, rafflecurrencystr, raffleplayers, raffleprize, rafflecurrency, rafflekeyword, rafflewinlist, rafflewinmsg
        global hiloactive, hilobet, hilorounds, hilouser, hiloopen, hilocard, hilocurrency, hilosuit, hilocurrencystr
        global roulettemin, roulettemax

        msginfo, username, messageo = re_chat.search(response).group(1, 2, 4)
        displayname = re.search(r"display-name=(.*?);", msginfo).group(1)
        message = re.sub(r" @", " ", messageo).lower()
        msglist = message.split()

        # master commands
        if ismaster():
            # --- true master commands ---
            if ismaster(True):
                # master rename command
                if textmatch(r"^!rename \w+ \w+"):
                    global renameconfirmation
                    olduser = msglist[1]
                    newuser = msglist[2]
                    # setup
                    if message != renameconfirmation:
                        if olduser == newuser:
                            chat("Both usernames provided are the same.")
                        else:
                            # check old username
                            olduserdbcount = 0
                            chatmsg = "Renaming " + olduser + ": "
                            if olduser in gold:
                                olduserdbcount += 1
                                chatmsg += shortnum(gold[olduser]) + " gold, "
                            if olduser in raregold:
                                olduserdbcount += 1
                                chatmsg += shortnum(raregold[olduser]) + " raregold, "
                            if olduser in slotsstats:
                                olduserdbcount += 1
                                chatmsg += str(slotsstats[olduser][0]) + " slots plays, "
                            if olduser in bjstats:
                                olduserdbcount += 1
                                chatmsg += str(bjstats[olduser][0]) + " Blackjack plays, "
                            if olduser in roulettestats:
                                olduserdbcount += 1
                                chatmsg += str(roulettestats[olduser][0]) + " Roulette plays, "
                            if olduser in senpais:
                                olduserdbcount += 1
                                chatmsg += str(senpais[olduser][2]) + " Senpai attempts, "
                            if olduser in vocaloids:
                                olduserdbcount += 1
                                chatmsg += str(vocaloids[olduser][1]) + " vocaloid attempts, "
                            if olduser in pets:
                                olduserdbcount += 1
                                chatmsg += str(pets[olduser][1]) + " pet attempts, "

                            if olduserdbcount == 0:
                                chat("User '" + olduser + "' is not in any database.")
                            else:
                                # check new username
                                newuserdbcount = 0
                                if newuser in gold:
                                    newuserdbcount += 1
                                if newuser in raregold:
                                    newuserdbcount += 1
                                if newuser in slotsstats:
                                    newuserdbcount += 1
                                if newuser in bjstats:
                                    newuserdbcount += 1
                                if newuser in roulettestats:
                                    newuserdbcount += 1
                                if newuser in senpais:
                                    newuserdbcount += 1
                                if newuser in vocaloids:
                                    newuserdbcount += 1
                                if newuser in pets:
                                    newuserdbcount += 1

                                chatmsg += " New name '" + newuser
                                if newuserdbcount > 0:
                                    chatmsg += "' already exists. Enter command again to confirm overwrite."
                                else:
                                    chatmsg += "'. Enter command again to confirm."
                                chat(chatmsg)
                                renameconfirmation = message
                    # confirm
                    else:
                        if olduser in gold:
                            gold[newuser] = gold[olduser]
                            del gold[olduser]
                        if olduser in raregold:
                            raregold[newuser] = raregold[olduser]
                            del raregold[olduser]
                        if olduser in slotsstats:
                            slotsstats[newuser] = slotsstats[olduser]
                            del slotsstats[olduser]
                        if olduser in bjstats:
                            bjstats[newuser] = bjstats[olduser]
                            del bjstats[olduser]
                        if olduser in roulettestats:
                            roulettestats[newuser] = roulettestats[olduser]
                            del roulettestats[olduser]
                        if olduser in senpais:
                            senpais[newuser] = senpais[olduser]
                            del senpais[olduser]
                        if olduser in vocaloids:
                            vocaloids[newuser] = vocaloids[olduser]
                            del vocaloids[olduser]
                        if olduser in pets:
                            pets[newuser] = pets[olduser]
                            del pets[olduser]
                        chat("Rename '" + olduser + "' to '" + newuser + "' complete.")
                        renameconfirmation = ""

                # master add/remove commands
                elif textmatch(r"^!master \w+ \w+"):
                    cmduser = msglist[2]
                    if msglist[1] == "add":
                        if cmduser in masterlist:
                            chat("'" + cmduser + "' is already set as a master.")
                        else:
                            masterlist.append(cmduser)
                            chat("'" + cmduser + "' has been set as a master.")

                    elif msglist[1] == "remove":
                        if cmduser in masterlist:
                            masterlist.remove(cmduser)
                            chat("'" + cmduser + "' has been removed as a master.")
                        else:
                            chat("'" + cmduser + "' is not a master.")
                    jdump("masterlist.txt", masterlist)
                # crash on demand
                elif message == "!divide by zero":
                    slotsenable = 1 / 0
                # restart
                elif message == "!restart":
                    chatp("Restarting")
                    sleep(1)
                    restart()
                # shut down
                elif message == "!shutdown":
                    global stayalive
                    savedata()
                    chat("Bye.")
                    sleep(1)
                    stayalive = False

            # --- general master commands ---
            # say something
            if textmatch(r"^!say ."):
                chat(re.search(r" (.+)", messageo).group(1))

            # master gold/raregold commands
            elif textmatch(r"^!(rare)?gold \w+ \w+"):
                cmdname = msglist[1]
                cmduser = msglist[2]

                if msglist[0] == "!gold":
                    currency = gold
                    currname = "gold"
                else:
                    currency = raregold
                    currname = "raregold"

                if textmatch(r"^!(rare)?gold \w+ \w+ \d+"):
                    cmdnumb = getnum(msglist[3])

                    if cmdname == "set":
                        if cmduser in currency:
                            diff = cmdnumb - currency[cmduser]
                        else:
                            diff = cmdnumb
                        currency[cmduser] = cmdnumb
                        chat(dname(cmduser) + " now has {:,} ".format(currency[cmduser]) + currname + " (" + shortnum(diff, signed=True) + ")")

                    elif cmdname == "add":
                        if cmduser == "online":
                            for user in activechat:
                                deal(currency, user, cmdnumb)
                            if currency is gold:
                                for user in activechat:
                                    paypetpercent(user, cmdnumb)
                            chat("Added " + shortnum(cmdnumb) + " " + currname + " to " + str(len(activechat)) + " active users.")
                        elif cmduser == "all":
                            # add active users to the database, in case they don't exist
                            for user in activechat:
                                deal(currency, user, 0)

                            for user in currency:
                                deal(currency, user, cmdnumb)
                            if currency is gold:
                                for user in currency:
                                    paypetpercent(user, cmdnumb)
                            chat("Added " + shortnum(cmdnumb) + " " + currname + " to all " + str(len(currency)) + " users in the database.")
                        else:
                            deal(currency, cmduser, cmdnumb)
                            if currency is gold:
                                paypetpercent(cmduser, cmdnumb)
                            chat(dname(cmduser) + " now has {:,} ".format(currency[cmduser]) + currname + " (+" + shortnum(cmdnumb) + ")")

                    elif cmdname == "remove":
                        if cmduser == "online":
                            for user in activechat:
                                deal(currency, user, -cmdnumb)
                            chat("Removed " + shortnum(cmdnumb) + " " + currname + " from all " + str(len(activechat)) + " active users.")
                        elif cmduser == "all":
                            # add active users to the database, in case they don't exist
                            for user in activechat:
                                deal(currency, user, 0)

                            for user in currency:
                                deal(currency, user, -cmdnumb)
                            chat("Removed " + shortnum(cmdnumb) + " " + currname + " from all " + str(len(currency)) + " users in the database.")
                        else:
                            deal(currency, cmduser, -cmdnumb)
                            chat(dname(cmduser) + " now has {:,} ".format(currency[cmduser]) + currname + " (-" + shortnum(cmdnumb) + ")")

                elif cmdname == "delete":
                    if cmduser in currency:
                        chat("Deleted " + cmduser + " (" + "{:,} ".format(currency[cmduser]) + currname + ") from the database.")
                        deal(currency, cmduser, -currency[cmduser])
                        del currency[cmduser]
                    else:
                        chat(cmduser + " is not in the database.")

            # master gamble commands
            elif textmatch(r"^!gamble open"):
                if not textmatch(r"^!gamble open \d+\.?\d*\w* \d+\.?\d*\w* \d+\.?\d*\w*"):
                    chat("Format is !gamble open <min> <max> <pay> <choice1> <choiceN> ...")
                elif gambleactive is True:
                    chat("A bet is already open.")
                elif len(msglist) < 7:
                    chat("At least 2 options must be given.")
                else:
                    # add choices to dictionary
                    for word in msglist[5:len(msglist)]:
                        gamblechoices[word] = 0
                    # check length again, in case of duplicates
                    if len(gamblechoices) < 2:
                        chat("There are duplicate bet options.")
                    else:
                        # initiate
                        gambleactive = True
                        gambleopen = True
                        gamblemin = getnum(msglist[2])
                        gamblemax = getnum(msglist[3])

                        # multiplier payout
                        if "x" in msglist[4]:
                            gamblemultiply = getnum(msglist[4])
                            payoutmsg = shortnum(gamblemultiply) + "x"
                        # flat payout
                        else:
                            gamblepay = getnum(msglist[4])
                            payoutmsg = shortnum(gamblepay)

                        # create string like [choice1], [choiceN] ...
                        chatmsg = "[" + "], [".join(sorted(gamblechoices)) + "]"

                        chat("Bet opened! Min bet: " + shortnum(gamblemin) + ", Max bet: " + shortnum(
                            gamblemax) + ", Payout: " + payoutmsg + ", Options: " + chatmsg)

            elif textmatch(r"^!gamble winner \w+"):
                gamblewinner = msglist[2]
                if gambleactive is False:
                    chat("No bet is currently active.")
                elif gamblewinner not in gamblechoices:
                    chat("'" + gamblewinner + "' is not a valid option.")
                else:
                    gamblewinners = []
                    gamblewinnerpot = 0
                    gambleloserpot = 0

                    # calculate pots and payouts
                    for user in gambleplayers:
                        casinobet = gambleplayers[user][0]
                        betchoice = gambleplayers[user][1]
                        if betchoice == gamblewinner:
                            gamblewinnerpot += casinobet
                        else:
                            gambleloserpot += casinobet
                            gambleplayers[user][0] *= -1

                    # calculate pot splits
                    for user in gambleplayers:
                        casinobet = gambleplayers[user][0]
                        if casinobet > 0:
                            # "however if both winners win but they bet diff amounts, so one winner bet 1000 and the other bet 1.
                            # both still get + 1000 but the pot split 99% of it goes to the 1000 better and 1% goes to the 1 gold better."  - hiso
                            if gamblepay > 0:
                                gambleplayers[user][0] = int(gamblepay + casinobet / gamblewinnerpot * gambleloserpot)
                            else:
                                gambleplayers[user][0] *= gamblemultiply
                            gamblewinners.append("[" + user + " +" + shortnum(gambleplayers[user][0]) + "]")

                    # pay winners, charge losers
                    for user in gambleplayers:
                        deal(gold, user, gambleplayers[user][0])

                    # announcement message
                    chatmsg1 = "'" + gamblewinner + "' is the winning option! "
                    if len(gamblewinners) == 0:
                        chatmsg1 += "All " + str(len(gambleplayers)) + " players lost! "
                    else:
                        chatmsg1 += str(len(gamblewinners)) + " of " + str(len(gambleplayers)) + " players won! "

                    chat(chatmsg1 + ", ".join(gamblewinners))

                    gamblereset()

            elif message == "!gamble close":
                if gambleactive is False:
                    chat("No bet is currently active.")
                elif gambleopen is False:
                    chat("Bet is already closed.")
                else:
                    gambleopen = False
                    chat("Bets closed. " + gamblesummary())

            elif message == "!gamble cancel":
                if gambleactive is False:
                    chat("No bet is currently active.")
                else:
                    gamblereset()
                    chat("Bet cancelled.")

            # master slots commands
            elif message == "!slots on":
                if slotsenable is True:
                    chat("Slots already enabled.")
                else:
                    slotsenable = True
                    chat("Slots enabled.")
            elif message == "!slots off":
                if slotsenable is False:
                    chat("Slots already disabled.")
                else:
                    slotsenable = False
                    chat("Slots disabled.")

            # master blackjack commands
            elif textmatch(r"^!bj \D+"):
                if msglist[1] == "on":
                    if bjenable is True:
                        chat("Blackjack already enabled.")
                    else:
                        bjenable = True
                        if bjactive is False and bjopen is False:
                            bjreset()
                            chat("Blackjack enabled. A new game will open in " + str(bjinterval) + "m.")
                        else:
                            chat("Blackjack enabled.")
                elif msglist[1] == "off":
                    if bjenable is False:
                        chat("Blackjack already disabled.")
                    else:
                        bjenable = False
                        chat("Blackjack disabled.")
                elif msglist[1] == "start":
                    if bjactive is True or bjopen is True:
                        chat("A Blackjack game is already running.")
                    else:
                        bjtimer = 1
                elif msglist[1] == "cancel":
                    if bjactive is True or bjopen is True:
                        bjactive = bjopen = False
                        bjreset()
                        chat("Blackjack game cancelled.")
                    else:
                        chat("There is no Blackjack game currently active.")

                elif textmatch(r"^!bj \w+ \d+"):
                    if bjactive is True or bjopen is True:
                        chat("A Blackjack game is already running.")
                    else:
                        cmduser = re.search(r"^!bj (\w+) \d+", message).group(1)
                        if cmduser in activechat or cmduser in raregold:
                            casinobet = getnum(msglist[2])
                            bjdesignate = [cmduser, casinobet]
                            bjopen = True
                            bjtimer = time() + 10
                            chat(dname(cmduser) + ", you have been challenged to a game of Blackjack with a bet of " + shortnum(
                                casinobet) + ". Type !bj accept to confirm " + choice(bjreactpos))
                        else:
                            chat("" + cmduser + " is not in the database.")
                else:
                    chat("Blackjack commands: 'on', 'off', 'start', 'cancel', '<user> <bet'.")

            # master raid commands
            elif textmatch(r"^!raid \w+"):
                global raidtimer, raidenable
                if msglist[1] == "on":
                    if raidenable is True:
                        chat("Raids already enabled.")
                    else:
                        if raidopen is False and raidactive is False:
                            raidreset()
                        raidenable = True
                        chat("Raids enabled.")
                elif msglist[1] == "off":
                    if raidenable is False:
                        chat("Raids already disabled.")
                    else:
                        raidenable = False
                        chat("Raids disabled.")
                elif msglist[1] == "start":
                    if raidopen is True or raidactive is True:
                        chat("A raid is already running.")
                    else:
                        raidtimer = 1
                else:
                    chat(dname() + " — Raid commands: 'on', 'off', 'start'.")
                return

            # master roulette commands
            elif textmatch(r"^!roulette \D+") and msglist[1] != "stats":
                global roulettetimer, rouletteenable, roulettemin, roulettemax
                if msglist[1] == "on":
                    if rouletteenable is True:
                        chat("Roulette already enabled.")
                    elif not (len(msglist) >= 4 and textmatch(r"^!roulette on \d+\.?\d*\w* \d+\.?\d*\w*")):
                        chat("Format is !roulette on <min> <max>")
                    else:
                        rouletteenable = True
                        roulettemin = getnum(msglist[2])
                        roulettemax = getnum(msglist[3])
                        if rouletteopen is False and rouletteactive is False:
                            roulettereset()
                            chat("Roulette enabled. A new game will open in " + str(rouletteinterval) + " minutes.")
                        else:
                            chat("Roulette enabled.")
                elif msglist[1] == "off":
                    if rouletteenable is False:
                        chat("Roulette already disabled.")
                    else:
                        rouletteenable = False
                        chat("Roulette disabled.")
                elif msglist[1] == "start":
                    if rouletteopen is True or rouletteactive is True:
                        chat("A game of roulette is already running.")
                    elif not (len(msglist) >= 4 and textmatch(r"^!roulette start \d+\.?\d*\w* \d+\.?\d*\w*")):
                        chat("Format is !roulette start <min> <max>")
                    else:
                        roulettemin = getnum(msglist[2])
                        roulettemax = getnum(msglist[3])
                        roulettetimer = 1

            # master raffle commands
            elif msglist[0] == "!raffle":
                if msglist[1] == "open":
                    if raffleactive is True:
                        chat("A raffle is already open.")
                    elif not textmatch(r"!raffle open \d+\S* (rare)?gold \w+"):
                        chat("Format is !raffle open <payout> <currency> <keyword> <optional win message>")
                    else:
                        raffleactive = True
                        raffleprize = getnum(msglist[2])
                        rafflekeyword = msglist[4]
                        if msglist[3] == "gold":
                            rafflecurrency = gold
                            rafflecurrencystr = "gold"
                        else:
                            rafflecurrency = raregold
                            rafflecurrencystr = "raregold"
                        if len(msglist) > 5:
                            rafflewinmsg = " ".join(messageo.split()[5:len(msglist)])
                        chat("The raffle is open! Type '" + rafflekeyword + "' for a chance to win " + shortnum(raffleprize) + " " + rafflecurrencystr + "!")

                elif msglist[1] == "draw":
                    if raffleactive is False:
                        chat("There is no raffle currently open.")
                    elif len(raffleplayers) == 0:
                        chat("There are no users in the raffle.")
                    elif len(raffleplayers) == 1:
                        chat("There is only one user in the raffle.")
                    else:
                        # XOR operation. get list of players in the raffle, but not in the winners list
                        raffleeligiblewinners = list(set(raffleplayers) ^ set(rafflewinlist))
                        if len(raffleeligiblewinners) == 0:
                            chat("Every user in the raffle has already won.")
                        else:
                            rafflewinner = SystemRandom().choice(raffleeligiblewinners)
                            rafflewinlist.append(rafflewinner)
                            deal(rafflecurrency, rafflewinner, raffleprize)
                            chat(dname(rafflewinner) + " wins " + shortnum(raffleprize) + " " + rafflecurrencystr + " from the raffle! " + rafflewinmsg)

                elif msglist[1] == "reset":
                    if raffleactive is False:
                        chat("There is no raffle currently open.")
                    else:
                        raffleplayers = []
                        rafflewinlist = []
                        chat("The raffle has been reset. Type '" + rafflekeyword + "' for a chance to win " + shortnum(
                            raffleprize) + " " + rafflecurrencystr + "!")

                elif msglist[1] == "close":
                    if raffleactive is False:
                        chat("There is no raffle currently open.")
                    else:
                        raffleactive = False
                        raffleplayers = []
                        rafflewinlist = []
                        rafflewinmsg = ""
                        chat("The raffle has been closed. Thanks for playing hisoScum")

                else:
                    chat("Raffle commands: 'open', 'draw', 'reset', 'close', 'info'")

            # master senpai commands
            elif textmatch(r"!senpai pay all"):
                numberpaid = 0
                for user in senpais:
                    if senpais[user][0] is True:
                        deal(gold, user, senpaigold)
                        deal(raregold, user, senpairaregold)
                        senpais[user][3] += senpaigold
                        senpais[user][4] += senpairaregold
                        numberpaid += 1
                chat("Paid {} gold and {} raregold to all {} Senpais.".format(shortnum(senpaigold), shortnum(senpairaregold), numberpaid))

            elif textmatch(r"!senpai pay online"):
                numberpaid = 0
                for user in activechat:
                    if senpais[user][0] is True:
                        deal(gold, user, senpaigold)
                        deal(raregold, user, senpairaregold)
                        senpais[user][3] += senpaigold
                        senpais[user][4] += senpairaregold
                        numberpaid += 1
                chat("Paid {} gold and {} raregold to {} active Senpais.".format(shortnum(senpaigold), shortnum(senpairaregold), numberpaid))

            elif textmatch(r"^!senpai pay \w+"):
                cmduser = msglist[2]
                if issenpai(cmduser):
                    deal(gold, cmduser, senpaigold)
                    deal(raregold, cmduser, senpairaregold)
                    senpais[cmduser][3] += senpaigold
                    senpais[cmduser][4] += senpairaregold
                    chat(dname(cmduser) + " now has {:,}".format(gold[cmduser]) + " gold (+" + shortnum(senpaigold) + ") and {:,}".format(
                        raregold[cmduser]) + " raregold (+" + shortnum(senpairaregold) + ") ")
                else:
                    chat(dname(cmduser) + " is not a Senpai.")

            elif textmatch(r"^!senpai draw"):
                senpaislist = []
                for user, userinfo in senpais.items():
                    if userinfo[0] is True and user in activechat:
                        senpaislist.append(user)
                if textmatch(r"^!senpai draw \d+"):
                    senpaidrawnum = getnum(msglist[2])
                else:
                    senpaidrawnum = 1

                if len(senpaislist) == 0:
                    chat("No senpais are currently active.")
                elif senpaidrawnum > len(senpaislist):
                    chat("There are only " + str(len(senpaislist)) + " senpais currently active.")
                elif senpaidrawnum == 1:
                    chat(dname(SystemRandom().choice(senpaislist)) + " has been chosen.")
                elif senpaidrawnum > 1:
                    senpaislist = SystemRandom().sample(senpaislist, senpaidrawnum)
                    chatmsg = []
                    for ss in senpaislist:
                        chatmsg.append(dname(ss))
                    sss = len(senpaislist) - 1
                    chat(", ".join(chatmsg[0:sss]) + ", and " + chatmsg[sss] + " have been chosen.")

            # master hilo commands
            elif msglist[0] == "!hilo":
                if len(msglist) > 1 and msglist[1] == "open":
                    # hilo start
                    if not textmatch(r"^!hilo open \w+ \d+ \d+\.?\d*\w* (gold|raregold)$"):
                        chat("Format is !hilo open <user> <rounds> <bet> <currency>")
                    else:
                        cmduser = msglist[2]
                        cmdnumb = getnum(msglist[4])
                        hilocurrencystr = msglist[5]
                        if hilocurrencystr == "gold":
                            hilocurrency = gold
                        else:
                            hilocurrency = raregold

                        if hiloactive is True:
                            chat("A game of Hi Lo is already active.")
                        # elif msglist[1] not in activechat:
                        #    chat("User " + dname(cmduser) + " is not here to play.")
                        elif cmduser not in hilocurrency:
                            chat("User " + dname(cmduser) + " doesn't have any " + hilocurrencystr + ".")
                        elif hilocurrency[cmduser] < cmdnumb:
                            chat("User " + dname(cmduser) + " doesn't have enough " + hilocurrencystr + " (" + shortnum(hilocurrency[cmduser]) + ").")
                        else:
                            hiloopen = True
                            hilouser = cmduser
                            # [current round, total rounds, bonus rounds]
                            hilorounds = [0, int(msglist[3]), 0]
                            hilobet = cmdnumb
                            chat(dname(hilouser) + ", you have been challenged to a game of Hi Lo with a bet of " + shortnum(
                                hilobet) + " " + msglist[5] + ". Type !hilo accept to confirm.")

                # hilo cancel
                elif message == "!hilo cancel":
                    if hiloactive is False and hiloopen is False:
                        chat("There is no game of Hi Lo currrently active.")
                    else:
                        hiloreset()
                        chat("The game of Hi Lo has been cancelled.")

            # master vocaloid commands
            elif textmatch(r"^!vocaloid pay \w+"):
                vocaloidname = msglist[2]
                paidusers = 0
                paiduserlist = []
                titleowners = 0
                if not isvocaloid(vocaloidname):
                    chat("'" + vocaloidname + "' is not a valid option.")
                else:
                    vocaloidpay = int(re.search(vocaloidname + r"=(\d+)", titlespay).group(1))

                    for user, info in vocaloids.items():
                        if info[0] == vocaloidname:
                            titleowners += 1
                            if user in activechat:
                                deal(gold, user, vocaloidpay)
                                paidusers += 1
                                paiduserlist.append(dname(user))

                    paiduserlist = ", ".join(paiduserlist)

                    if paidusers == 0:
                        if titleowners > 0:
                            chat("None of the {} users who own the {} title were here to receive payment.".format(titleowners, vocaloidname.capitalize()))
                        else:
                            chat("Nobody owns the {} title.".format(vocaloidname.capitalize()))
                    else:
                        chat("Paid {} gold to {} of {} users with the {} title: {}."
                             .format(shortnum(vocaloidpay), paidusers, titleowners, vocaloidname.capitalize(), paiduserlist))

            # master pet commands
            elif textmatch(r"^!pet list"):
                petlist = []
                for user, petinfo in sorted(pets.items(), key=lambda m: m[1][3], reverse=True):
                    if petinfo[0] is True:
                        petlist.append("[{}: Lvl{} {}]".format(dname(user, False), petinfo[3], petinfo[2]))

                chat("There are {} users with pets: {}".format(len(petlist), ", ".join(petlist)))
                return

            elif textmatch(r"^!pet draw"):
                petlist = []
                for user, userinfo in pets.items():
                    if userinfo[0] is True and user in activechat:
                        petlist.append(user)
                if textmatch(r"^!pet draw \d+"):
                    petdrawnum = getnum(msglist[2])
                else:
                    petdrawnum = 1

                if len(petlist) == 0:
                    chat("No pets are currently active.")
                elif petdrawnum > len(petlist):
                    chat("There are only " + str(len(petlist)) + " pets currently active.")
                elif petdrawnum == 1:
                    chat(dname(SystemRandom().choice(petlist)) + " has been chosen.")
                elif petdrawnum > 1:
                    petlist = SystemRandom().sample(petlist, petdrawnum)
                    chatmsg = []
                    for ss in petlist:
                        chatmsg.append(dname(ss))
                    sss = len(petlist) - 1
                    chat(", ".join(chatmsg[0:sss]) + ", and " + chatmsg[sss] + " have been chosen.")
                return

            # master mute command
            elif textmatch(r"^!mute"):
                if casinomute is False:
                    chatp("Casino muted.")
                    casinomute = True
                else:
                    chatp("Casino already muted.")
            elif textmatch(r"^!unmute"):
                if casinomute is True:
                    chatp("Casino unmuted.")
                    casinomute = False
                else:
                    chatp("Casino already unmuted.")

                # --- master commands end ---

        # non-lurker activity tracking (for gold/raregold payouts)
        if not {username} & {irc_nick, irc_chan}:
            activechat[username] = [time() + activetime, displayname]
            if username not in gold:
                deal(gold, username, startergold)
            if username not in raregold:
                deal(raregold, username, startergold)

        # --- general commands start ---
        if textmatch(r"^!\w") and (nogames() or ismaster()):
            command = msglist[0].lstrip("!")
            # basic gold commands
            if command == "gold" and len(msglist) <= 2:
                if textmatch(r"^!gold \w+"):
                    cmduser = msglist[1]
                else:
                    cmduser = username

                if cmduser == "top5":
                    # top 5 richest
                    chatmsg = []
                    for e, user in enumerate(sorted(gold.items(), key=lambda m: m[1], reverse=True)):
                        if e < 5 or (e < len(gold) < 5):
                            chatmsg.append("[" + dname(user[0]) + ": " + shortnum(user[1]) + "]")
                        else:
                            break
                    chat(" — ".join(chatmsg))
                else:
                    if cmduser in gold:
                        for rank, usergold in enumerate(sorted(gold.items(), key=lambda m: m[1], reverse=True)):
                            if usergold[0] == cmduser:
                                chat(dname(cmduser) + " — {:,}".format(usergold[1]) + " gold (#" + str(rank + 1) + ")")
                                break
                    else:
                        chat(dname(cmduser) + " is not in the database.")

            elif command == "raregold" and len(msglist) <= 2:
                if textmatch(r"^!raregold \w+"):
                    cmduser = msglist[1]
                else:
                    cmduser = username

                if cmduser == "top5":
                    # top 5 richest
                    chatmsg = []
                    for e, user in enumerate(sorted(raregold.items(), key=lambda m: m[1], reverse=True)):
                        if e < 5 or (e < len(raregold) < 5):
                            chatmsg.append("[" + dname(user[0]) + ": " + shortnum(user[1]) + "]")
                        else:
                            break
                    chat(" — ".join(chatmsg))
                else:
                    if cmduser in raregold:
                        for rank, usergold in enumerate(sorted(raregold.items(), key=lambda m: m[1], reverse=True)):
                            if usergold[0] == cmduser:
                                chat(dname(cmduser) + " — {:,}".format(usergold[1]) + " raregold (#" + str(rank + 1) + ")")
                                break
                    else:
                        chat(dname(cmduser) + " is not in the database.")

            # give raregold to another user
            elif textmatch(r"^!give \w+ \d+") and hasraregold() and nodictban(bangiveraregold, "give raregold"):
                cmduser = msglist[1]
                cmdnumb = getnum(msglist[2])
                if cmduser not in raregold and cmduser not in activechat:
                    chat(dname() + " — User " + cmduser + " is not in the database.")
                elif cmduser not in activechat:
                    chat(dname() + " — User " + cmduser + " is not here to receive.")
                elif raregold[username] < cmdnumb:
                    chat(dname() + " — You don't have enough raregold (" + shortnum(raregold[username]) + ")")
                elif cmdnumb == 0:
                    pass
                elif username == cmduser:
                    pass
                else:
                    dictban(bangiveraregold, username, givecooldown)
                    deal(raregold, cmduser, cmdnumb)
                    deal(raregold, username, -cmdnumb)
                    chat(dname() + " gave " + shortnum(cmdnumb) + " raregold to " + dname(cmduser) + " [" + shortnum(raregold[cmduser]) + "].")

            # convert gold to raregold
            elif textmatch(r"^!convert \d+") and hasgold():
                cmdnumb = getnum(msglist[1])
                if gold[username] < cmdnumb:
                    chat(dname() + " — You don't have enough gold (" + shortnum(gold[username]) + ")")
                elif cmdnumb % goldconvert != 0:
                    chat(dname() + " — You must convert a multiple of {:,}".format(goldconvert))
                elif cmdnumb == 0:
                    pass
                else:
                    convertedraregold = cmdnumb / goldconvert * raregoldconvert
                    deal(gold, username, -cmdnumb)
                    deal(raregold, username, convertedraregold)
                    chat(dname() + " — You now have " + shortnum(gold[username]) + " gold(-" + shortnum(
                        cmdnumb) + ") and " + shortnum(raregold[username]) + " raregold(+" + shortnum(convertedraregold) + ")")

            # slots commands
            elif command == "slots" and len(msglist) >= 2:
                if textmatch(r"^!slots (\d|all)") and slotsenable and nodictban(bancasino, "gamble"):
                    casinobet = getnum(msglist[1])
                    if hasraregold(casinobet):
                        # game
                        slotresult, casinobet, slotscode, goldbonus = slots(dname(), casinobet)
                        # avoid debt
                        if (casinobet < 0) and (raregold[username] < abs(casinobet)):
                            casinobet = raregold[username] * -1
                        # results
                        if goldbonus > 0:
                            casinobet += goldbonus
                            slotresult += " (+" + shortnum(goldbonus) + " cate bonus)"
                        deal(raregold, username, casinobet)
                        # cooldown scaling based on raregold owned
                        if username in raregold and raregold[username] > 1e6:
                            dictban(bancasino, username, slotscooldown * log10(raregold[username]) / 3)
                        else:
                            dictban(bancasino, username, slotscooldown)
                        slotsstatslog(casinobet, slotscode)
                        chat(slotresult + raregolddiff(username, casinobet))

                elif msglist[1] == "stats":
                    if textmatch(r"^!slots stats \w+"):
                        sstatsuser = msglist[2]
                    else:
                        sstatsuser = username

                    if textmatch(r"^!slots stats all"):
                        slotsstatsall = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        for user in slotsstats:
                            # add individual elements in same order
                            slotsstatsall = [sum(x) for x in zip(slotsstatsall, slotsstats[user])]
                        chat("Slots stats for ALL PLAYERS — Plays: {}, Raregold won: {}, Raregold lost: {}, KA-POWs: {}, 0x: {}, 2x: {}, "
                             "2x/2x: {}, 3x: {}, 3x/2x: {}, 4x: {}, 5x: {}"
                             .format(slotsstatsall[0], shortnum(slotsstatsall[1]), shortnum(slotsstatsall[2]), *slotsstatsall[3:11]))

                    elif sstatsuser in slotsstats:
                        chat("Slots stats for {} — Plays: {}, Raregold won: {}, Raregold lost: {}, KA-POWs: {}, 0x: {}, 2x: {}, "
                             "2x/2x: {}, 3x: {}, 3x/2x: {}, 4x: {}, 5x: {}"
                             .format(dname(sstatsuser), slotsstats[sstatsuser][0], shortnum(slotsstats[sstatsuser][1]),
                                     shortnum(slotsstats[sstatsuser][2]), *slotsstats[sstatsuser][3:11]))
                    else:
                        chat(dname(sstatsuser) + " is not in the database.")

            # blackjack bet
            elif textmatch(r"^!bj (\d+|all)") and bjopen is True and username not in bjqueue:
                casinobet = getnum(msglist[1])
                if hasraregold(casinobet):
                    bjqueue.append(username)
                    bjplayers[username] = Bjplayer(dname(), casinobet, bjpayout)

            # blackjack designate
            elif message == "!bj accept" and bjopen is True and bjdesignate is not None and username == bjdesignate[0]:
                bjqueue.append(username)
                bjplayers[username] = Bjplayer(dname(), bjdesignate[1], bjpayout)

            # blackjack stats
            elif textmatch(r"^!bj stats"):
                if textmatch(r"^!bj stats \w+"):
                    bjstatsuser = msglist[2]
                else:
                    bjstatsuser = username

                if textmatch(r"^!bj stats all"):
                    bjstatsall = [0, 0, 0, 0, 0, 0, 0, 0]
                    for user in bjstats:
                        # add individual elements in same order
                        bjstatsall = [sum(x) for x in zip(bjstatsall, bjstats[user])]
                    chat("Blackjack stats for ALL PLAYERS — Plays: {}, Raregold won: {}, Raregold lost: {}, Wins: {}, Losses: {}, Ties: {}, Busts: {}, BJs: {}"
                         .format(bjstatsall[0], shortnum(bjstatsall[1]), shortnum(bjstatsall[2]), *bjstatsall[3:8]))

                elif bjstatsuser in bjstats:
                    # 0: total plays, 1: raregold won, 2: raregold lost, 3: wins, 4: losses, 5: ties, 6: busts, 7: BJs
                    chat("Blackjack stats for {} — Plays: {}, Raregold won: {}, Raregold lost: {}, Wins: {}, Losses: {}, Ties: {}, Busts: {}, BJs: {}"
                         .format(dname(bjstatsuser), bjstats[bjstatsuser][0], shortnum(bjstats[bjstatsuser][1]), shortnum(bjstats[bjstatsuser][2]),
                                 *bjstats[bjstatsuser][3:8]))
                else:
                    chat(dname(bjstatsuser) + " is not in the database.")

            # version
            elif command == "casinoversion":
                print("Casino " + casinoversion)

            # raffle info
            elif message == "!raffle info":
                if raffleactive is False:
                    chat("There is no raffle currently open.")
                else:
                    chat("Raffle info — Prize: {} {}, Players: {}, Winners: {}, Keyword: '{}'"
                         .format(shortnum(raffleprize), rafflecurrencystr, len(raffleplayers), len(rafflewinlist), rafflekeyword))

            # title rolling
            elif command == "roll" and len(msglist) >= 2:
                # senpai roll
                if msglist[1] == "senpai":
                    if issenpai(username):
                        chat(dname() + " — You already have Senpai status.")
                    elif not hasgold(senpaicost, True):
                        pass
                    elif not nodictban(bantitle, "roll for a title"):
                        pass
                    else:
                        deal(gold, username, -senpaicost)
                        dictban(bantitle, username, titlecooldown)
                        rngint = SystemRandom().randint(1, senpaiodds)
                        # count number of attempts
                        if username in senpais:
                            senpais[username][2] += 1
                        else:
                            # [status, timestamp, attempts, gold, raregold]
                            senpais[username] = [False, 1e10, 1, 0, 0]
                        attempts = senpais[username][2]
                        # fail
                        if rngint != senpaiodds:
                            chat("{} — You roll {}/{}. {} {}".format(dname(), rngint, senpaiodds, rollfail(attempts), golddiff(username, -senpaicost)))
                        # win
                        else:
                            if attempts > 1:
                                chatmsg = "It only took " + str(attempts) + " attempts."
                            else:
                                chatmsg = "You won on the first try!"
                            chat("{} —  You roll {}/{}. Congratulations! hisoChamp You have officially earned Senpai status! {}"
                                 .format(dname(), rngint, senpaiodds, chatmsg))
                            senpais[username][0] = True
                            senpais[username][1] = round(time(), 2)
                            jdump("senpais.txt", senpais)

                # vocaloid roll
                elif isvocaloid(msglist[1]):
                    if username in vocaloids and vocaloids[username][0] == msglist[1]:
                        chat(dname() + " — You already have that title.")
                    elif not hasgold(titlecost, True):
                        pass
                    elif not nodictban(bantitle, "roll for a title"):
                        pass
                    else:
                        deal(gold, username, -titlecost)
                        dictban(bantitle, username, titlecooldown)
                        rngint = SystemRandom().randint(1, titleodds)
                        # count number of attempts
                        if username in vocaloids:
                            vocaloids[username][1] += 1
                        else:
                            # [title, attempts]
                            vocaloids[username] = [None, 1]
                        attempts = vocaloids[username][1]
                        # fail
                        if rngint != titleodds:
                            chat("{} — You roll {}/{}. {} {}".format(dname(), rngint, titleodds, rollfail(attempts), golddiff(username, -titlecost)))
                        # win
                        else:
                            if attempts > 1:
                                chatmsg = "It only took " + str(attempts) + " attempts."
                            else:
                                chatmsg = "You won on the first try!"
                            chat("{} —  You roll {}/{}. Congratulations! hisoChamp "
                                 "You have officially earned the {} title! {}".format(dname(), rngint, titleodds, msglist[1].capitalize(), chatmsg))
                            vocaloids[username][0] = msglist[1]
                            jdump("vocaloids.txt", vocaloids)

                # pet roll
                elif msglist[1] == "pet":
                    if username in pets and pets[username][0] is True:
                        chat(dname() + " — You already have a pet.")
                    elif not hasgold(petcost, True):
                        pass
                    elif not nodictban(banpet, "roll for a pet"):
                        pass
                    else:
                        deal(gold, username, -petcost)
                        dictban(banpet, username, petcooldown)
                        rngint = SystemRandom().randint(1, petodds)
                        # count number of attempts
                        if username in pets:
                            pets[username][1] += 1
                        else:
                            # [0: status, 1: attempts, 2: name, 3: level, 4: gold]
                            pets[username] = [False, 1, "", 0, 0]
                        attempts = pets[username][1]
                        # fail
                        if rngint != petodds:
                            chat("{} — You roll {}/{}. {} {}".format(dname(), rngint, petodds, rollfail(attempts), golddiff(username, -petcost)))
                        # win
                        else:
                            if attempts > 1:
                                chatmsg = "It only took " + str(attempts) + " attempts."
                            else:
                                chatmsg = "You won on the first try!"
                            chat("{} —  You roll {}/{}. Congratulations! hisoChamp You have officially earned a pet! {}"
                                 .format(dname(), rngint, petodds, chatmsg))
                            pets[username][0] = True
                            jdump("pets.txt", pets)

            # sub daily pay
            elif command == "payme":
                if "subscriber/" in msginfo:
                    if nodictban(dailies, "recieve daily pay"):
                        # ban until midnight
                        dailies[username] = nextday()
                        deal(gold, username, subdaily)
                        chat(dname(username) + " now has {:,}".format(gold[username]) + " gold (+" + shortnum(subdaily) + ")")
                        jdump("dailies.txt", dailies)
                else:
                    deal(gold, username, -subdaily)
                    chat(dname() + " — Nice try, non-subscriber. Now hand over " + shortnum(subdaily) + " gold. Thank you very much hisoScum")

            # senpai stats
            elif textmatch(r"^!senpai stats"):
                if len(msglist) > 2:
                    cmduser = msglist[2]
                else:
                    cmduser = username

                if cmduser == "all":
                    senpaicount = 0
                    for user, userinfo in senpais.items():
                        if userinfo[0] is True:
                            senpaicount += 1
                    chat("There are currently {} Senpais and {} users who have tried and failed.".format(senpaicount, len(senpais) - senpaicount))

                else:
                    if cmduser not in senpais:
                        chat("User " + dname(cmduser) + " is not in the database.")
                    elif not issenpai(cmduser):
                        chat(dname(cmduser) + " still has no senpai status after " + str(senpais[cmduser][2]) + " attempts.")
                    else:
                        for rank, senpaitime in enumerate(sorted(senpais.items(), key=lambda m: m[1][1])):
                            if senpaitime[0] == cmduser:
                                chat("{} earned Senpai on {} ({}, #{}) in {} attempts and earned {} gold and {} raregold."
                                     .format(dname(cmduser), strftime("%B %d %Y", localtime(senpais[cmduser][1])), deltatime(senpais[cmduser][1]),
                                             str(rank + 1), str(senpais[cmduser][2]), shortnum(senpais[cmduser][3]), shortnum(senpais[cmduser][4])))
                                break

            # vocaloid stats (title)
            elif textmatch(r"^!vocaloid title \w+"):
                cmdname = msglist[2]
                titleowners = 0

                if not isvocaloid(cmdname):
                    chat(dname() + " — '" + cmdname + "' is not a valid option.")
                else:
                    for user, info in vocaloids.items():
                        if info[0] == cmdname:
                            titleowners += 1

                    if titleowners == 0:
                        chat("Nobody owns the {} title.".format(cmdname.capitalize()))
                    elif titleowners == 1:
                        chat("There is 1 person who owns the {} title.".format(cmdname.capitalize()))
                    else:
                        chat("There are {} users who own the {} title.".format(titleowners, cmdname.capitalize()))

            # vocaloid stats (user)
            elif textmatch(r"^!vocaloid stats"):
                if len(msglist) > 2:
                    cmduser = msglist[2]
                else:
                    cmduser = username

                if cmduser not in vocaloids:
                    chat("User {} is not in the database.".format(dname(cmduser)))
                else:
                    title, attempts = vocaloids[cmduser]
                    if vocaloids[cmduser][0] is None:
                        chat("{} still has no vocaloid title after {} attempts.".format(dname(cmduser), attempts))
                    else:
                        chat("{} earned the {} title after {} attempts.".format(dname(cmduser), title.capitalize(), attempts))

            # pet commands
            # [0: status, 1: attempts, 2: name, 3: level, 4: gold]
            elif command == "pet":
                # pet stats
                if textmatch(r"^!pet stats"):
                    if len(msglist) > 2:
                        cmduser = msglist[2]
                    else:
                        cmduser = username

                    if cmduser == "all":
                        petcount = 0
                        for user, userinfo in pets.items():
                            if userinfo[0] is True:
                                petcount += 1
                        pethighlvl = max(pets.items(), key=lambda p: p[1][3])[0]
                        pethighgold = max(pets.items(), key=lambda p: p[1][4])[0]
                        pethighattempts = max(pets.items(), key=lambda p: p[1][1])[0]
                        chat("There are {} pet owners and {} users who tried and failed. {}'s pet is the highest level at {}. "
                             "{}'s pet has the most gold at {}. {} has made the most attempts at {}."
                             .format(petcount, len(pets) - petcount, dname(pethighlvl, False), pets[pethighlvl][3], dname(pethighgold, False),
                                     shortnum(pets[pethighgold][4]), dname(pethighattempts, False), pets[pethighattempts][1]))

                    else:
                        if cmduser not in pets:
                            chat("User {} is not in the database.".format(dname(cmduser)))
                        else:
                            if pets[cmduser][0] is False:
                                chat("{} still has no pet after {} attempts.".format(dname(cmduser), pets[cmduser][1]))
                            else:
                                chat("{}'s pet — Name: {}, Level: {}, Gold: {}, Attempts: {}"
                                     .format(dname(cmduser), pets[cmduser][2], pets[cmduser][3], shortnum(pets[cmduser][4]), pets[cmduser][1]))

                # pet naming
                elif textmatch(r"^!pet rename \w+"):
                    if haspet():
                        newpetname = re.search(r"^!pet rename (\w+)", messageo).group(1)
                        if len(newpetname) > 39:
                            chat(dname() + " — Pet name cannot be longer than 39 characters.")

                        # no name
                        elif pets[username][2] == "":
                            pets[username][2] = newpetname
                            chat(dname() + " — Congratulations! Your pet's new name is " + newpetname + ".")
                        # has name already, renaming
                        else:
                            # exponential function
                            renamecost = int(100 * 1.39 ** (pets[username][3] - 1))
                            if hasraregold(renamecost, True):
                                deal(raregold, username, -renamecost)
                                pets[username][2] = newpetname
                                chat("{} — Your pet has been renamed to {} {}".format(dname(), newpetname, raregolddiff(username, -renamecost)))

                # pet level
                elif textmatch(r"^!pet level"):
                    if haspet():
                        level = pets[username][3]
                        # exponential function
                        levelcost = int(100 * 1.39 ** (level - 1))
                        # level up cost check
                        if textmatch(r"^!pet level$"):
                            # having enough money
                            if username in raregold and raregold[username] >= levelcost:
                                chat("{} — {}'s current level is {}. Cost to level up is {}. You have {} raregold."
                                     .format(dname(), pets[username][2], pets[username][3], shortnum(levelcost), shortnum(raregold[username])))
                            # not having enough money
                            else:
                                chat("{} — {}'s current level is {}. Cost to level up is {}. You need {} more raregold."
                                     .format(dname(), pets[username][2], pets[username][3], shortnum(levelcost), shortnum(levelcost - raregold[username])))
                        # level up
                        elif textmatch(r"^!pet level up") and hasraregold(levelcost, True) and nodictban(banpetlevel, "level your pet"):
                            if pets[username][2] == "":
                                chat(dname() + " — You must first give a name to your pet.")
                            else:
                                deal(raregold, username, -levelcost)
                                pets[username][3] += 1
                                dictban(banpetlevel, username, petlevelcooldown * 60 * 1.0377 ** (level - 1))
                                chat("{} — Congratulations! {} is now level {}! {}"
                                     .format(dname(), pets[username][2], level + 1, raregolddiff(username, -levelcost)))
                                jdump("pets.txt", pets)

                # invalid command
                else:
                    chat(dname() + " — Pet commands: 'stats', 'level', 'level up', 'rename'")

            # roulette stats
            elif textmatch(r"^!roulette stats"):
                if textmatch(r"^!roulette stats \w+"):
                    rstatsuser = msglist[2]
                else:
                    rstatsuser = username

                if textmatch(r"^!roulette stats all"):
                    roulettestatsall = [0, 0, 0, 0, 0]
                    for user in roulettestats:
                        # add individual elements in same order
                        roulettestatsall = [sum(x) for x in zip(roulettestatsall, roulettestats[user])]
                    chat("Roulette stats for ALL PLAYERS — Plays: {}, Gold won: {}, Gold lost: {}, Wins: {}, Losses: {}"
                         .format(roulettestatsall[0], shortnum(roulettestatsall[1]), shortnum(roulettestatsall[2]), *roulettestatsall[3:5]))

                elif rstatsuser in roulettestats:
                    chat("Roulette stats for {} — Plays: {}, Gold won: {}, Gold lost: {}, Wins: {}, Losses: {}"
                         .format(dname(rstatsuser), roulettestats[rstatsuser][0], shortnum(roulettestats[rstatsuser][1]),
                                 shortnum(roulettestats[rstatsuser][2]), *roulettestats[rstatsuser][3:5]))
                else:
                    chat(dname(rstatsuser) + " is not in the database.")

            # emote stats
            elif textmatch(r"^!\s?hiso\w+"):
                # selecting year
                if textmatch(r"hiso\w+ \d+"):
                    cmdyear = re.search(r"hiso\w+ (\d+)", message).group(1)
                # else use current year
                else:
                    cmdyear = strftime("%Y")
                emotename = re.search(r"hiso(\S+)", messageo).group(1)
                if cmdyear in emotestats and emotename in emotestats[cmdyear]:
                    chat("{:,} {}s posted in {} hiso{}".format(emotestats[cmdyear][emotename], emotename, cmdyear, emotename))

            # lottery
            elif command == "lottery" and nodictban(banlottery, "play the lottery") and hasgold(lotterycost, True):
                banlottery[username] = nextday()
                lottdigits = len(str(lotteryodds))
                # use date as seed, pad with leading zeroes
                lottdraw = str(Random(strftime("%D")).randint(0, lotteryodds)).zfill(lottdigits)
                # use date and username as seed, pad with leading zeroes
                lottnum = str(Random(strftime("%D") + username).randint(0, lotteryodds)).zfill(lottdigits)
                if lottnum != lottdraw:
                    deal(gold, username, -lotterycost)
                    chat("{} — Today's lottery draw is {}. Your number is {}. Try again another day {}."
                         .format(dname(), lottdraw, lottnum, golddiff(username, -lotterycost)))
                else:
                    deal(gold, username, lotteryprize)
                    chat("{} — Today's lottery draw is {}. Your number is {}. Congratulations! hisoChamp {}."
                         .format(dname(), lottdraw, lottnum, golddiff(username, lotteryprize)))

            # --- general commands end ---

            # --- shared cooldown commands start ---
            elif time() > commandtimer or ismaster():
                # dice roll
                if textmatch(r"^!d\s?\d+"):
                    cmdnumb = int(re.search(r"\d+", message).group(0))
                    if 1e12 > cmdnumb > 1:
                        commandtimer = time() + commandcooldown
                        cmdnumb = SystemRandom().randint(1, cmdnumb)
                        chat(dname() + " rolls a {:,}".format(cmdnumb))

                # calculator
                elif command == "calc":
                    chatmsg = None
                    calcoutput = 0

                    # basic operations
                    if textmatch(r"^!calc (\d+\.?\d*)\s?([+\-x*/^])\s?(\d+\.?\d*)"):
                        calcnumb1, calcoperation, calcnumb2 = re.search(r"^!calc (\d+\.?\d*)\s?([+\-x*/^])\s?(\d+\.?\d*)", message).group(1, 2, 3)
                        if "." in calcnumb1:
                            calcnumb1 = float(calcnumb1)
                        else:
                            calcnumb1 = int(calcnumb1)
                        if "." in calcnumb2:
                            calcnumb2 = float(calcnumb2)
                        else:
                            calcnumb2 = int(calcnumb2)

                        # neither number is zero or one
                        if not {0, 1} & {calcnumb1, calcnumb2}:
                            if calcoperation == "+":
                                calcoutput = calcnumb1 + calcnumb2
                            elif calcoperation == "-":
                                calcoutput = calcnumb1 - calcnumb2
                            elif calcoperation == "x" or calcoperation == "*":
                                calcoutput = calcnumb1 * calcnumb2
                            elif calcoperation == "/":
                                calcoutput = calcnumb1 / calcnumb2
                            elif calcoperation == "^":
                                # avoid hangs
                                if calcnumb2 < 100:
                                    calcoutput = calcnumb1 ** calcnumb2

                            calcoutput = round(calcoutput, 2)
                            if float(calcoutput).is_integer():
                                calcoutput = int(calcoutput)
                            chatmsg = "{:,} {} {:,} = {:,}".format(calcnumb1, calcoperation, calcnumb2, calcoutput)

                    # square root
                    elif textmatch(r"^!calc sqrt\s?\d+"):
                        calcnumb1 = int(re.search(r"^!calc sqrt\s?(\d+)", message).group(1))
                        calcoutput = round(calcnumb1 ** 0.5, 2)
                        chatmsg = "√{:,} = {}".format(calcnumb1, calcoutput)

                    # output answer, if not too long
                    if chatmsg is not None and len(chatmsg) < 50:
                        chat(chatmsg)
                        commandtimer = time() + commandcooldown

                # casino command
                elif command == "casino":
                    commandtimer = time() + commandcooldown
                    cmdnumb = SystemRandom().randint(1, 39)
                    if cmdnumb == 1:
                        if "mod=1" not in msginfo:
                            chat(".timeout " + username + " 39")
                            chat(dname() + " got banned from the casino hisoCate")
                    elif cmdnumb == 2:
                        casinosteal = SystemRandom().randint(1, 100)
                        casinostealamount = int(casino * casinosteal / 100)
                        if casinostealamount <= 0:
                            chat(dname() + " tried stealing the casino's donations, but there wasn't any money to steal hisoChamp")
                        else:
                            deal(raregold, username, casinostealamount)
                            chat(dname() + " steals " + str(casinosteal) + "% of the casino's donation reserve and gains " + shortnum(
                                casinostealamount) + " raregold hisoBruh")
                            casino -= casinostealamount
                    elif cmdnumb == 3:
                        deal(raregold, username, 1)
                        chat(dname() + " wins 1 raregold. Congratulations hisoChamp")
                    elif cmdnumb == 4:
                        chat("hisoCate")
                    else:
                        if username in raregold and raregold[username] > 100:
                            casinodonation = int(raregold[username] * SystemRandom().randint(1, 39) / 100)
                            deal(raregold, username, -casinodonation)
                            chat(dname() + " donates " + shortnum(casinodonation) + " raregold to the casino. Thank you very much hisoScum")
                            casino += casinodonation

                # bang
                elif textmatch(r"^!bang \w+"):
                    banguser = msglist[1]
                    if banguser in activechat:
                        # create seeds using both usernames and the date
                        bangchance = Random(Random(username).random() + Random(banguser).random() + Random(strftime("%D")).random()).randint(0, 100)
                        if bangchance == 0:
                            chat("There is a {}% chance that {} and {} are banging tonight.".format(bangchance, dname(), dname(banguser)))
                        elif bangchance == 8 or 80 <= bangchance <= 89:
                            chat("There is an {}% chance that {} and {} are banging tonight hisoMoan".format(bangchance, dname(), dname(banguser)))
                        else:
                            chat("There is a {}% chance that {} and {} are banging tonight hisoMoan".format(bangchance, dname(), dname(banguser)))
                        commandtimer = time() + commandcooldown

                # hitman
                elif textmatch(r"^!hitman") and len(activechat) > 0:
                    if username in gold and gold[username] >= hitmancost:
                        deal(gold, username, -hitmancost)
                        hittarget = SystemRandom().choice(list(activechat))
                        chat("Pepega pepeGun KAPOW " + dname(hittarget) + " — You were taken down by " + dname(username) + "'s hitman.")
                    else:
                        gold[username] = 0
                        chat("Pepega pepeGun KAPOW " + dname(username) + " — You didn't have enough gold.")
                        hittarget = username
                    chat(".timeout " + hittarget + " 39")
                    commandtimer = time() + commandcooldown

                # weather
                elif command == "weather":
                    try:
                        chat(getweather())
                    except:
                        chat("Failed to retrieve weather data.")
                    commandtimer = time() + commandcooldown

                # --- shared cooldown commands end ---

        # --- high importance commands start ---

        # gamble play
        if msglist[0] == "!bet" and gambleactive:
            # bet info
            if message == "!bet info":
                if gambleopen is True:
                    chatmsg = "Bets are still open. "
                else:
                    chatmsg = "Bets are closed. "

                chat(chatmsg + gamblesummary())

            # place bet
            elif textmatch(r"^!bet \d+\.?\d*\w* .+"):
                casinobet = getnum(msglist[1])
                betchoice = msglist[2]
                if gambleopen is False:
                    chat(dname() + " — Bets are currently closed.")
                elif casinobet < gamblemin:
                    chat(dname() + " — Minimum bet is " + shortnum(gamblemin) + " gold.")
                elif casinobet > gamblemax:
                    chat(dname() + " — Maximum bet is " + shortnum(gamblemax) + " gold.")
                elif betchoice not in gamblechoices:
                    chat(dname() + " — '" + betchoice + "' is not a valid option.")
                elif username in gambleplayers:
                    chat(dname() + " — You already placed a bet.")
                elif not hasgold(casinobet):
                    pass
                else:
                    gambleplayers[username] = [casinobet, betchoice]
                    gamblechoices[betchoice] += 1
            else:
                chat(dname() + " — Format is !bet <amount> <choice>")

        # raid join
        elif msglist[0] == "!raid" and haspet() and raidopen is True:
            if username in raidplayers:
                chat(dname() + " — You already joined the raid.")
            elif pets[username][2] == "":
                chat(dname() + " — You haven't given your pet a name yet.")
            else:
                raidplayers.append(username)

        # roulette join
        elif textmatch(r"^!roulette \d+") and len(msglist) > 2 and rouletteopen is True:
            roulettebet = getnum(msglist[1])
            rbettype = msglist[2]
            if username in rouletteplayers:
                chat(dname() + " — You already joined the roulette table.")
            elif roulettebet < roulettemin:
                chat(dname() + " — Minimum bet is " + shortnum(roulettemin) + " gold.")
            elif roulettebet > roulettemax:
                chat(dname() + " — Maximum bet is " + shortnum(roulettemax) + " gold.")
            elif not (rbettype in roulettebets or rbettype in roulettebetsalt or (rbettype.isdigit() and 0 <= int(rbettype) <= 36)):
                chat("{} — Valid bets are {}.".format(dname(), ", ".join(roulettebets)))
            elif not hasgold(roulettebet):
                pass
            else:
                if rbettype in roulettebetsalt:
                    rbettype = roulettebets[roulettebetsalt.index(rbettype)]
                rouletteplayers[username] = [roulettebet, rbettype]

        # blackjack play
        elif bjactive is True and len(bjqueue) > 0 and username == bjqueue[0] and bjplayers[username].standing is False and textmatch(
                r"(hit|double|stand|stay)"):
            if "hit" in message:
                bjplayers[username].hit()
            elif "double" in message:
                if raregold[username] < (bjplayers[username].bet * 2):
                    chat(dname() + " — You don't have enough raregold to double down.")
                else:
                    bjplayers[username].hit(double=True)
            elif "stand" in message or "stay" in message:
                bjplayers[username].stand()

            if bjplayers[username].standing is True:
                bjtimer = time() + seqtime
            else:
                bjtimer = time() + bjtimeout
            chat(bjplayers[username].bjoutput)

        # hilo start
        elif hiloopen is True and bjactive is False and username == hilouser and textmatch(r"^!hilo accept"):
            if (hilocurrency is gold and hasgold(hilobet, True)) or (hilocurrency is raregold and hasraregold(hilobet, True)):
                hiloopen = False
                hiloactive = True
                hilocard = SystemRandom().randint(0, 12)
                hilosuit = SystemRandom().randint(0, 3)
                chat("A game of Hi Lo with " + dname() + " has started! The first card is a " + suits[hilosuit] + deck[hilocard] + ".")

        # hilo play
        elif hiloactive is True and username == hilouser and textmatch(r"(hi|lo)"):
            hilorounds[0] += 1
            roundstogo = hilorounds[1] + hilorounds[2] - hilorounds[0]

            newcard = SystemRandom().randint(0, 12)
            newsuit = SystemRandom().randint(0, 3)

            # compare new card with current card
            if newcard < hilocard:
                chatmsg = dname() + " draws " + suits[newsuit] + deck[newcard] + ". It's lower than " + suits[hilosuit] + deck[hilocard] + ". "
                if "hi" in message:
                    hilocontinue = False
                else:
                    hilocontinue = True
            elif newcard > hilocard:
                chatmsg = dname() + " draws " + suits[newsuit] + deck[newcard] + ". It's higher than " + suits[hilosuit] + deck[hilocard] + ". "
                if "hi" in message:
                    hilocontinue = True
                else:
                    hilocontinue = False
            else:
                chatmsg = dname() + " draws " + suits[newsuit] + deck[newcard] + ". It's equal to " + suits[hilosuit] + deck[hilocard] + ". "
                if issenpai(username):
                    chatmsg += "Senpais can try again. "
                    hilorounds[2] += 1
                    roundstogo += 1
                    hilocontinue = True
                else:
                    hilocontinue = False

            # determine if game continues or ends
            if hilocontinue is True:
                hilocard = newcard
                hilosuit = newsuit
                if roundstogo > 1:
                    chat(chatmsg + str(roundstogo) + " more rounds to go!")
                elif roundstogo == 1:
                    chat(chatmsg + "One more round to go!")
                # win, game end
                else:
                    hilobet = int(hilobet / (0.807 ** (hilorounds[1] - 1)))
                    deal(hilocurrency, username, hilobet)
                    if hilocurrency is gold:
                        chat(chatmsg + "You won all " + str(hilorounds[1]) + " rounds! " + golddiff(username, hilobet))
                    else:
                        chat(chatmsg + "You won all " + str(hilorounds[1]) + " rounds! " + raregolddiff(username, hilobet))
                    hiloreset()
            # lose, game end
            else:
                deal(hilocurrency, username, -hilobet)
                if hilocurrency is gold:
                    chat(chatmsg + "You lose. " + golddiff(username, -hilobet))
                else:
                    chat(chatmsg + "You lose. " + raregolddiff(username, -hilobet))
                hiloreset()

        # raffle entry
        elif raffleactive is True and rafflekeyword in message and username not in raffleplayers:
            raffleplayers.append(username)

        # --- high importance commands end ---

        # easter
        elif bjactive is raidactive is rouletteactive is False and rng(0.00039):
            if "rigged" in message:
                chat("PJSalt")
            elif "all in" in message and slotsenable is True:
                chat("The next person who goes all in is guaranteed to win! hisoChamp")
            elif "i can do it" in message:
                chat("You cate do it hisoCate")
            elif "i can do this" in message:
                chat("You cate do this hisoCate")
            elif "i can do that" in message:
                chat("You cate do that hisoCate")
            elif "senpai" in message and username != irc_nick:
                chat("The next person who rolls for Senpai is guaranteed to win! hisoChamp")

        # offlinemode username change for testing purposes
        elif offlinemode is True and textmatch(r"^!username \w+"):
            global offlineusername
            offlineusername = msglist[1]

        # pyramid breaker
        elif len(msglist) == 2 and msglist[0] == msglist[1]:
            pyramidcache = [username, msglist[0]]
        elif len(msglist) >= 3 and username == pyramidcache[0] and msglist[0] == msglist[1] == msglist[2] == pyramidcache[1]:
            chatp("hisoMini")
            pyramidcache = ["", ""]
        else:
            pyramidcache = ["", ""]

        # count emotes in normal message
        countemotes(msginfo, messageo)

    # subscriber gold payment
    elif re_usernotice.search(response):
        msginfo, messageo = re_usernotice.search(response).group(1, 2)
        username = re.search(r"login=(.+?);", msginfo).group(1)

        # normal subs
        if re.search(r"msg-id=(sub|resub);", msginfo):
            # send chat message depending on sub type
            if "msg-id=resub" in msginfo:
                # count sub months
                submonths = re.search(r"msg-param-(cumulative-)?months=(\d+)", msginfo).group(2)
                if submonths == "0":
                    chatmsg = "Thanks for subbing, " + dname(username)
                else:
                    chatmsg = "Thanks for subbing " + submonths + " times, " + dname(username)
            else:
                submonths = 1
                chatmsg = "Thanks for subbing, " + dname(username)

            # identify sub tier and pay accordingly
            if "msg-param-sub-plan=3000" in msginfo:
                subpay = subpay3
            elif "msg-param-sub-plan=2000" in msginfo:
                subpay = subpay2
            else:
                subpay = subpay1
            deal(gold, username, subpay)
            chatmsg += " You now have {:,} gold (+{}).".format(gold[username], shortnum(subpay))

            # number of cates in message equal to sub months
            c = 0
            while c < int(submonths):
                c += 1
                chatmsg += " hisoCate"

            chat(chatmsg)

        # gift subs
        elif re.search(r"msg-id=subgift;", msginfo):
            global giftsubtimer
            giftsubtimer = time() + 1

            # identify sub tier before placing in queue
            if "msg-param-sub-plan=3000" in msginfo:
                subtier = 3
            elif "msg-param-sub-plan=2000" in msginfo:
                subtier = 2
            else:
                subtier = 1

            # check if in queue before placing in queue
            if username in giftsubqueue:
                # modify, add gift count
                giftsubqueue[username][0] += 1
            else:
                # new entry. [gift count, tier]
                giftsubqueue[username] = [1, subtier]

        # count emotes in sub message
        countemotes(msginfo, messageo)

    else:
        if response == "PING :tmi.twitch.tv":
            serversend("PONG :tmi.twitch.tv")
            global pingtimer
            pingtimer = time() + 360
        elif "RECONNECT" in response:
            serverconnect()


# MESSAGE INCOMING
def messageinque():
    while threadsenable:
        while offlinemode is False:
            try:
                response = (s.recv(1024).decode("utf-8")).splitlines()
                msginque.extend(response)
            except UnicodeDecodeError:
                console("Error decoding message. Message ignored.")

        while offlinemode is True:
            response = input()
            # chat message
            msginque.append("@X;display-name={};emotes=X;X :{}!X@X.tmi.twitch.tv PRIVMSG #{} :{}".format(offlineusername, offlineusername, irc_chan, response))

            # full custom server message
            # msginque.append(response)


# MESSAGE OUTGOING
def messageoutque():
    while threadsenable:
        # avoid global ban
        sleep(0.35)
        if len(msgoutque) > 0:
            # send >CHAT< message to the server
            msgsend = msgoutque.popleft()
            if offlinemode is nochat is False:
                serversend("PRIVMSG #{} :{}".format(irc_chan, msgsend))
            else:
                console(msgsend)


# MESSAGE PROCESSING
def processing():
    while threadsenable:
        if len(msginque) > 0:
            msgprocess(msginque.popleft())
        else:
            sleep(0.1)


# BOT TIMERS
def timereponse():
    global bjopen, bjenable, bjactive, bjtimer, bjdeal, bjqueue, bjdesignate, bjplayers, bjdealerturns
    global giftsubqueue
    global raidtimer, raidopen, raidactive, raidplayers, raidlevel, raidboss, raidmsgque
    global roulettetimer, rouletteopen, rouletteactive, rouletteplayers, rlmsgque

    nextpayout = time() + paytimer
    prevgold = dict(gold)
    prevraregold = dict(raregold)

    while threadsenable:
        sleep(0.5)

        # if last ping over 6min ago, restart
        if time() > pingtimer and offlinemode is False:
            restart()

        # gold timer
        if time() > nextpayout:
            nextpayout += paytimer
            if len(activechat) >= chatminimum:
                # IN THIS THREAD:
                # 1: MAKE A COPY OF THE DICTIONARY
                # 2: ITERATE THE COPY
                # 3: PROCESS THE ORIGINAL

                # pay active chatters
                activechatcopy = dict(activechat)
                for user, lurktime in activechatcopy.items():
                    if time() < lurktime[0]:
                        deal(gold, user, goldpayout)
                        deal(raregold, user, raregoldpayout)

                        paypetpercent(user, goldpayout)
                    else:
                        del activechat[user]

            if prevgold != gold or prevraregold != raregold:
                savedata()
                prevgold = dict(gold)
                prevraregold = dict(raregold)

        # gift sub timer
        if time() > giftsubtimer and len(giftsubqueue) > 0:
            for user, data in giftsubqueue.items():
                giftcount = data[0]
                subtier = data[1]

                # build message
                if giftcount == 1:
                    chatmsg = "Thanks for gifting a sub, " + dname(user) + " hisoCate"
                else:
                    chatmsg = "Thanks for gifting " + str(giftcount) + " subs, " + dname(user)
                    c = 0
                    while c < int(giftcount):
                        c += 1
                        chatmsg += " hisoCate"

                # identify sub tier and pay accordingly
                if subtier == 3:
                    giftsubpay = subpay3 * giftcount
                    deal(gold, user, giftsubpay)
                elif subtier == 2:
                    giftsubpay = subpay2 * giftcount
                    deal(gold, user, giftsubpay)
                else:
                    giftsubpay = subpay1 * giftcount
                    deal(gold, user, giftsubpay)

                chatmsg += " You now have {:,} gold (+{}).".format(gold[user], shortnum(giftsubpay))
                chat(chatmsg)

                giftsubqueue = {}

        # blackjack timers
        if time() > bjtimer and raidopen is False and raidactive is False:
            # game starting
            if (bjenable is True or bjtimer == 1) and bjopen is False and bjactive is False:
                bjopen = True
                bjtimer = time() + 30
                chat("The Blackjack♠ table has opened! " + choice(bjreactpos) + " You have 30 seconds to join with !bj <bet>")
            # close joins and start a game if there are any players
            elif bjopen is True:
                bjopen = False
                # length of queue is always 1 higher than number of players, since it starts with a ""
                if len(bjqueue) > 1:
                    bjactive = True
                    bjtimer = time() + seqtime
                    bjdeal = Bjdealer()
                    bjdealerturns = deque(bjdeal.bjoutput)
                    if len(bjqueue) == 2:
                        chat(dname(bjqueue[1]) + " has joined the Blackjack table! My first card is a " + bjdeal.hand[0])
                    else:
                        chat(str(len(bjqueue) - 1) + " players have joined the Blackjack table! My first card is a " + bjdeal.hand[0])
                else:
                    bjtimer = time() + bjinterval * 60
                    chatmsg2 = ""
                    if bjenable is True:
                        chatmsg2 = " Another game will open again in " + str(bjinterval) + "m."
                    if bjdesignate is None:
                        chat("Nobody joined the Blackjack table " + choice(bjreactneg) + " " + chatmsg2)
                    else:
                        chat(dname(bjdesignate[0]) + " did not accept the Blackjack offer in time " + choice(bjreactneg))

            # game play
            elif bjactive is True:
                # sequence through players' turns
                if len(bjqueue) > 0:
                    bjtimer = time() + bjtimeout
                    chatmsg2 = ""

                    # start of game/first player
                    # the first in the queue is a ""
                    if bjqueue[0] == "":
                        bjqueue.popleft()
                        # if multiple players have joined
                        if len(bjqueue) != 1:
                            chatmsg2 = choice(bjmsgfirst) + " " + dname(bjqueue[0]) + "! "
                        # else, one player has joined
                        else:
                            chatmsg2 = dname(bjqueue[0]) + "'s "
                        chat(chatmsg2 + bjplayers[bjqueue[0]].bjoutput)

                        if bjplayers[bjqueue[0]].blackjack is True:
                            bjtimer = time() + seqtime

                    # multiple players remaining
                    elif len(bjqueue) > 2:
                        if bjplayers[bjqueue[0]].standing is False:
                            chatmsg2 = choice(bjmsgtimeup) + ", " + dname(bjqueue[0]) + "! "
                        bjqueue.popleft()
                        chat(chatmsg2 + choice(bjmsgnext) + " " + dname(bjqueue[0]) + "! " + bjplayers[bjqueue[0]].bjoutput)

                        if bjplayers[bjqueue[0]].blackjack is True:
                            bjtimer = time() + seqtime

                    # one more player left after the current one
                    elif len(bjqueue) == 2:
                        if bjplayers[bjqueue[0]].standing is False:
                            chatmsg2 = choice(bjmsgtimeup) + ", " + dname(bjqueue[0]) + "! "
                        bjqueue.popleft()
                        chat(chatmsg2 + choice(bjmsgfinal) + " " + dname(bjqueue[0]) + "! " + bjplayers[bjqueue[0]].bjoutput)

                        if bjplayers[bjqueue[0]].blackjack is True:
                            bjtimer = time() + seqtime

                    # final player's turn is over
                    elif len(bjqueue) == 1:
                        if bjplayers[bjqueue[0]].standing is False:
                            chat(choice(bjmsgtimeup) + ", " + dname(bjqueue[0]) + "! ")
                        bjqueue.popleft()
                        bjtimer = 0
                        if len(bjplayers) > 1:
                            bjdealerturns.appendleft(
                                "All players have finished! It's my turn " + choice(bjreactpos) + " First card is " + bjdeal.hand[0] + "...")
                        else:
                            bjdealerturns.appendleft("It's my turn " + choice(bjreactpos) + " First card is " + bjdeal.hand[0] + "...")

                # dealer's turn
                else:
                    bjtimer = time() + seqtime
                    # check if all players busted. assume true at first
                    bjallbust = True
                    for user, bjplayervar in bjplayers.items():
                        if bjplayervar.bust is False:
                            bjallbust = False
                            break

                    # if all players busted, skip dealer's turn entirely
                    if bjallbust is True:
                        bjdealerturns = []
                        # extra message for multiple players
                        if len(bjplayers) > 1:
                            chat("Everyone went KAPOW I win it all Jebaited")

                    # sequence through the dealer's hits, one message at a time
                    if len(bjdealerturns) > 0:
                        chat(bjdealerturns.popleft())

                    # game finish
                    else:
                        bjwinners = {}
                        bjties = []
                        # analyze results
                        for user, bjplayervar in bjplayers.items():
                            # dealer is bust and player isn't
                            if bjdeal.bust is True and bjplayervar.bust is False:
                                bjwin = True
                            # player has higher value and isn't bust
                            elif bjdeal.value < bjplayervar.value <= 21:
                                bjwin = True
                            # player has BJ and dealer doesn't
                            elif bjdeal.blackjack is False and bjplayervar.blackjack is True:
                                bjwin = True

                            # player has same value as dealer, neither are bust, both or neither have BJ
                            elif (bjdeal.value == bjplayervar.value <= 21) and (bjdeal.blackjack == bjplayervar.blackjack):
                                bjwin = None
                                bjties.append(user)

                            # otherwise, player loses
                            else:
                                bjwin = False

                            # payouts
                            if bjwin is True:
                                deal(raregold, user, bjplayervar.bet)
                                bjwinners[user] = "[" + dname(user) + " +" + shortnum(bjplayervar.bet) + "]"
                            elif bjwin is False:
                                deal(raregold, user, -bjplayervar.bet)

                            # log stats
                            bjstatslog(bjwin, user, bjplayervar)

                        # write stats to disk here, outside the loop
                        jdump("bjstats.txt", bjstats)

                        # concluding message
                        if len(bjplayers) > 1:
                            # if multiple players
                            # winners
                            if len(bjwinners) > 0:
                                if len(bjwinners) == 1:
                                    chatmsg1 = "Here is the weiner " + choice(bjreactneg) + " "
                                else:
                                    chatmsg1 = "Here are the " + str(len(bjwinners)) + " weiners " + choice(bjreactneg) + " "

                                bjwinnerslist = []
                                chatmsg2 = ""
                                for user, msg in bjwinners.items():
                                    bjwinnerslist.append(msg)
                                    chatmsg2 = chatmsg1 + ", ".join(bjwinnerslist)

                                chat(chatmsg2)

                            # no winners
                            # there is already a message written earlier when everyone is bust, so we don't do it here
                            elif bjallbust is False:
                                if len(bjties) == 1:
                                    chat("Nobody won! " + choice(bjreactpos) + " Though " + dname(bjties[0]) + " has tied.")
                                elif len(bjties) > 1:
                                    chat("Nobody won! " + choice(bjreactpos) + " Though " + str(len(bjties)) + " players have tied.")
                                else:
                                    chat("Everyone lost! I keep it all Jebaited")
                        else:
                            # else only one player
                            # convert dictionary into list, then index it to find the player name
                            cmduser = list(bjplayers.items())[0][0]

                            if len(bjwinners) > 0:
                                chat(dname(cmduser) + " wins " + choice(bjreactneg) + " " + raregolddiff(username, bjplayers[cmduser].bet))
                            elif len(bjties) > 0:
                                chat("Looks like we end in a tie, " + dname(cmduser) + " " + choice(bjreactneg))
                            else:
                                chat("You lose, " + dname(cmduser) + "! " + choice(bjreactpos) + " " + raregolddiff(username, -bjplayers[cmduser].bet))

                        # reset
                        bjreset()

                        sleep(4)
                        if bjenable is True:
                            chat("Another Blackjack table will open again in " + str(bjinterval) + "m.")

        # raid timers
        if time() > raidtimer and bjopen is bjactive is False:
            # raid prep start (timer is set to 1 when manually starting)
            if (raidenable or raidtimer == 1) and raidopen is False and raidactive is False:
                raidopen = True
                raidtimer = time() + 30
                raidboss = SystemRandom().choices(raidbosslist, raidbossweight, k=1)[0]
                if raidboss == "hisokeee":
                    raidlevel = 100
                else:
                    raidlevel = raidbosslist.index(raidboss) * 10 + SystemRandom().randint(0, 9)
                chat("A raid boss has appeared! It's a Lv.{} {} ! You have 30 seconds to send in your pet with !raid".format(raidlevel, raidboss))

            # start raid
            elif raidopen is True:
                raidopen = False
                if len(raidplayers) == 0:
                    for user in raregold:
                        raregold[user] -= int(raregold[user] * raidstealignore)
                    chat("Nobody joined the raid. " + raidboss + " roams free and steals raregold from everyone!")
                    raidreset()
                else:
                    raidactive = True
                    raidtimer = time() + seqtime
                    if len(raidplayers) > 1:
                        SystemRandom().shuffle(raidplayers)
                        chat("The raid against Lv.{} {} has started! {} pets have entered the battle! Which ones will survive and bring back the loot?"
                             .format(raidlevel, raidboss, len(raidplayers)))
                    else:
                        chat("The raid against Lv.{} {} has started! Only one pet entered the battle! Will it survive and bring back the loot?"
                             .format(raidlevel, raidboss))

                    # process all players
                    raidwinnerslist = []
                    raidwinnerslvlsum = 0
                    for user in raidplayers:
                        userpetname = pets[user][2]
                        userpetlevel = pets[user][3]
                        # calculate odds (artificial sigmoid function)
                        petleveldelta = userpetlevel - raidlevel
                        raidodds = 0.5 / (2 ** (abs(petleveldelta) / 10))
                        if petleveldelta >= 0:
                            raidodds = 1 - raidodds
                        raidoddspercent = round(raidodds * 100, 1)
                        # if player win
                        if rng(raidodds):
                            raidwinnerslist.append(user)
                            raidwinnerslvlsum += userpetlevel
                            raidmsgque.append("Lv.{} {} survives the attack! ({}%)".format(userpetlevel, userpetname, raidoddspercent))
                        # else lose
                        else:
                            raidmsgque.append("Lv.{} {} falls in battle! ({}%)".format(userpetlevel, userpetname, raidoddspercent))

                    # create final message, process pay
                    if len(raidwinnerslist) == 0:
                        for user in raregold:
                            raregold[user] -= int(raregold[user] * raidstealwipe)
                        raidmsgque.append("The entire raid wiped! " + raidboss + " steals raregold from everyone!")
                    else:
                        # determine total payout
                        if raidlevel < 100:
                            # parabolic function
                            raidpayout = raidlevel ** 2 * 10
                        else:
                            raidpayout = 500000
                        # pay split is proprotional to pet's level
                        raidwinnersmsglist = []
                        for user in raidwinnerslist:
                            raidpayoutsplit = int(raidpayout * pets[user][3] / raidwinnerslvlsum)
                            paypet(user, raidpayoutsplit)
                            raidwinnersmsglist.append("[Lv.{} {} +{}]".format(pets[user][3], pets[user][2], shortnum(raidpayoutsplit)))
                        raidmsgque.append("The raid battle against Lv.{} {} is over. {} of {} pets survived! Here is the share of the gold: {}"
                                          .format(raidlevel, raidboss, len(raidwinnerslist), len(raidplayers), ", ".join(raidwinnersmsglist)))

            # raid over. cycle through all messages
            elif raidactive is True:
                raidtimer = time() + seqtime
                if len(raidmsgque) > 0:
                    chat(raidmsgque.popleft())
                else:
                    raidreset()

        # roulette timers
        if time() > roulettetimer and bjopen is bjactive is raidopen is raidactive is False:
            # roulette prep start (timer is set to 1 when manually starting)
            if (rouletteenable or roulettetimer == 1) and rouletteopen is False and rouletteactive is False:
                rouletteopen = True
                roulettetimer = time() + 30
                chat("The Roulette table has opened! {} Min bet: {}, Max bet: {}. You have 30 seconds to join with !roulette <amount> <type>"
                     .format(choice(bjreactpos), shortnum(roulettemin), shortnum(roulettemax)))

            # start roulette
            elif rouletteopen is True:
                rouletteopen = False
                if len(rouletteplayers) == 0:
                    chat("Nobody joined the roulette. " + choice(bjreactneg) + " .")
                    roulettereset()
                else:
                    rouletteactive = True
                    roulettetimer = time() + seqtime
                    # count bet types
                    rlbets = {}
                    for rluser, rlbett in rouletteplayers.items():
                        rlbett = rlbett[1]
                        if rlbett not in rlbets:
                            rlbets[rlbett] = 1
                        else:
                            rlbets[rlbett] += 1
                    # list the counts of bet types
                    rlbetsstr = []
                    for rlbett, rlnum in rlbets.items():
                        rlbetsstr.append(rlbett.capitalize() + ": " + str(rlnum))
                    # announce, generate final number, use number as seed for messages
                    chat("The game of Roulette begins! {} players have joined the table! [{}]".format(len(rouletteplayers), ", ".join(rlbetsstr)))
                    rnum = SystemRandom().randint(-1, 36)
                    rlmsgque.append("The ball rolls around the spinning roulette wheel. Which number will it land on?")
                    rlmsgque.append("The ball {} {}.".format(SystemRandom().choice(rouletterolls), roulettecolour(Random(rnum).randint(-1, 36))))
                    rlmsgque.append("The ball {} {}.".format(SystemRandom().choice(roulettestops), roulettecolour(Random(rnum + 38).randint(-1, 36))))
                    rlmsgque.append("The ball lands on " + roulettecolour(rnum) + "!")

                    # process all players
                    rlwinnerslist = []
                    for rluser, betdata in rouletteplayers.items():
                        bettype = betdata[1]
                        # check if win and determine pay multiplier
                        if (bettype == str(rnum)) or (bettype == "00" and rnum == -1):
                            rlbetmult = 35
                        elif bettype == "green" and -1 <= rnum <= 0:
                            rlbetmult = 17
                        elif bettype == "basket" and -1 <= rnum <= 3:
                            rlbetmult = 6
                        elif rnum > 0 and ((bettype == "c1" and rnum % 3 == 1) or (bettype == "c2" and rnum % 3 == 2) or
                                           (bettype == "c3" and rnum % 3 == 0) or (bettype == "d1" and 1 <= rnum <= 12) or
                                           (bettype == "d2" and 13 <= rnum <= 24) or (bettype == "d3" and 25 <= rnum <= 36)):
                            rlbetmult = 2
                        elif rnum > 0 and ((bettype == "low" and 1 <= rnum <= 18) or (bettype == "high" and 19 <= rnum <= 36) or
                                           (bettype == "red" and rnum in red) or (bettype == "black" and rnum in black) or
                                           (bettype == "even" and rnum % 2 == 0) or (bettype == "odd" and rnum % 2 == 1)):
                            rlbetmult = 1
                        else:
                            rlbetmult = -1
                        # calculate pay
                        rlbet = betdata[0] * rlbetmult
                        # if player win, add to list
                        if 0 < rlbetmult < 35:
                            rlwinnerslist.append("[{} ({}) +{}]".format(dname(rluser, False), bettype.capitalize(), shortnum(rlbet)))
                        elif rlbetmult == 35:
                            rlwinnerslist.append(emojize("[{} :sparkles: +{}]".format(dname(rluser, False), shortnum(rlbet))))

                        deal(gold, rluser, rlbet)
                        roulettestatslog(rluser, rlbet)

                    # save log, create final message
                    jdump("roulettestats.txt", roulettestats)
                    if len(rlwinnerslist) == 0:
                        rlmsgque.append("All the Roulette players lost!")
                    else:
                        rlmsgque.append("{} of {} players won: {}".format(len(rlwinnerslist), len(rouletteplayers), ", ".join(rlwinnerslist)))

            # roulette over. cycle through all messages
            elif rouletteactive is True:
                roulettetimer = time() + seqtime
                if len(rlmsgque) > 0:
                    chat(rlmsgque.popleft())
                else:
                    if rouletteenable is True:
                        chat("A new game will open in " + str(rouletteinterval) + " minutes.")
                    roulettereset()


# initiate threads
processthread = threading.Thread(target=processing, name="message-process", daemon=True)
messageinthread = threading.Thread(target=messageinque, name="message-in", daemon=True)
messageoutthread = threading.Thread(target=messageoutque, name="message-out", daemon=True)
timerthread = threading.Thread(target=timereponse, name="timer", daemon=True)

threadlist = [processthread, messageoutthread, timerthread, messageinthread]

if offlinemode is False:
    serverconnect()
    postcate()
else:
    print("Offline mode enabled")

print("hisokocasino by Kelerik")
print(casinoversion)
print("Python 3.7")

# start threads
messageinthread.start()
processthread.start()
messageoutthread.start()
timerthread.start()

# stay alive
while stayalive is True:
    sleep(1)
    # monitor all other threads. if any are dead, shut everything down
    for t in threadlist:
        if not t.is_alive():
            savedata()

            chatp("Error in #" + irc_chan + str(t))
            sleep(1)
            threadsenable = False
