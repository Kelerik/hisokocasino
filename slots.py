from collections import Counter
from random import SystemRandom
from configloader import slotsfaces, kapowchance, slotsodds, kapowpenalty, catebonus

profitratio = 2 - 3 * slotsodds
slotface = []
# load faces from config
for f in slotsfaces:
    # check in case of extra spaces
    if f != "":
        slotface.append(f)


def slots(playername, bet):
    slot = SystemRandom().sample(slotface, 5)

    if SystemRandom().random() < kapowchance:
        slot[SystemRandom().randint(0, 4)] = "KAPOW"

    winlevel = 0

    while (winlevel < 6) and (SystemRandom().random() < slotsodds):
        winlevel += 1

    # random pair
    if winlevel == 1:
        matchselect = SystemRandom().sample(range(5), 2)
        slot[matchselect[0]] = slot[matchselect[1]]

    # random two pair
    elif winlevel == 2:
        matchselect = SystemRandom().sample(range(5), 4)
        slot[matchselect[0]] = slot[matchselect[1]]
        slot[matchselect[2]] = slot[matchselect[3]]

    # random triple
    elif winlevel == 3:
        matchselect = SystemRandom().sample(range(5), 3)
        slot[matchselect[0]] = slot[matchselect[1]] = slot[matchselect[2]]

    # random full house
    elif winlevel == 4:
        matchselect = SystemRandom().sample(range(5), 5)
        slot[matchselect[0]] = slot[matchselect[1]]
        slot[matchselect[2]] = slot[matchselect[3]] = slot[matchselect[4]]

    # random quad
    elif winlevel == 5:
        matchselect = SystemRandom().sample(range(5), 4)
        slot[matchselect[0]] = slot[matchselect[1]] = slot[matchselect[2]] = slot[matchselect[3]]

    # random quint
    elif winlevel == 6:
        matchselect = SystemRandom().sample(range(5), 5)
        slot[matchselect[0]] = slot[matchselect[1]] = slot[matchselect[2]] = slot[matchselect[3]] = slot[matchselect[4]]

    result = " ".join(slot) + " — "

    # ***** ANALYZE RESULTS ****************************************************
    # list of matching faces, numbered from highest to lowest
    facecount = Counter(slot)
    # output format: Counter({'red': 4, 'blue': 2})

    # ***** PROCESS RESULT CODE *****
    # KAPOW = fail
    if "KAPOW" in facecount:
        resultcode = -facecount["KAPOW"]
    else:
        resultcode = 0
        for face, n in facecount.items():
            if n > 1:
                # squared to produce unique numbers
                resultcode += n ** 2

    # ***** PROCESS FINAL OUTPUT MESSAGE AND BET *****
    # -n: number of KAPOW
    # 0: no matches
    # 4: 2x
    # 8: 2x/2x
    # 9: 3x
    # 13: 3x/2x
    # 16: 4x
    # 25: 5x
    goldbonus = 0

    if resultcode < 0:
        result += "KA-POW! You're out of luck, " + playername + ". "
        bet *= -kapowpenalty
    elif resultcode == 0:
        result += "Too bad, " + playername + "! Better luck next time. "
        bet *= -1
    else:
        result += playername
        if resultcode == 4:
            result += " gets two matching faces"
            bet /= slotsodds ** 0
        elif resultcode == 8:
            result += " gets two pairs"
            bet /= slotsodds ** (1 * profitratio)
        elif resultcode == 9:
            result += " gets three matching faces"
            bet /= slotsodds ** (2 * profitratio)
        elif resultcode == 13:
            result += " gets a full house"
            bet /= slotsodds ** (3 * profitratio)
        elif resultcode == 16:
            result += " gets four matching faces"
            bet /= slotsodds ** (4 * profitratio)
        elif resultcode == 25:
            result += " gets five matching faces"
            bet /= slotsodds ** (5 * profitratio)
        else:
            result += "Error. Code " + str(resultcode)
            bet = 0
            return result, int(bet), resultcode

        if "hisoCate" in facecount:
            goldbonus = bet * facecount["hisoCate"] * catebonus

        result += "! "

    return result, int(bet), resultcode, int(goldbonus)
