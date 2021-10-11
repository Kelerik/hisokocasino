from random import SystemRandom, choice
from randomlists import *


class Bjplayer:
    def __init__(self, displayname, bet, blackjackbonus):
        self.drawcard = None
        self.name = displayname
        self.hand = []
        self.value = 0
        self.aces = 0
        self.bet = bet
        self.standing = False
        self.bust = False
        self.blackjack = False

        self.draw()
        self.draw()

        # checking for blackjack occurs here at the start
        # player's messages are created one string at a time. dealer's messages are all created in a list at once
        if self.value == 21:
            self.blackjack = True
            self.standing = True
            self.bet = int(self.bet * blackjackbonus)
            self.bjoutput = "Starting hand: " + "".join(self.hand) + " (BJ) " + choice(bjreactneg)
        else:
            self.bjoutput = "Starting hand: " + "".join(self.hand) + " (" + str(self.value) + ")"

    def draw(self):
        self.drawcard = SystemRandom().choice(bjdeck)
        self.hand.append(self.drawcard[0])
        self.value += self.drawcard[1]
        if self.drawcard[1] == 11:
            self.aces += 1
        # if hand is over 21, convert aces into values of 1 until either all aces are used or hand is under 21
        while self.aces > 0 and self.value > 21:
            self.aces -= 1
            self.value -= 10

    def hit(self, double=False):
        self.draw()
        if double is True:
            self.bet *= 2
            doublemsg = " doubles the bet " + choice(bjreactpos)
            self.standing = True
        else:
            doublemsg = ""

        if self.value < 21:
            if double is True:
                self.bjoutput = self.name + doublemsg + " draws " + self.drawcard[0] + ". Final hand: " + "".join(
                    self.hand) + " (" + str(self.value) + ")"
            else:
                self.bjoutput = self.name + doublemsg + " draws " + self.drawcard[0] + ". Current hand: " + "".join(
                    self.hand) + " (" + str(self.value) + ")"
        elif self.value == 21:
            # no checking for blackjack here
            self.standing = True
            self.bjoutput = self.name + doublemsg + " draws " + self.drawcard[0] + ". Final hand: " + "".join(
                self.hand) + " (" + str(self.value) + ") " + choice(bjreactneg)
        elif self.value > 21:
            self.bust = True
            self.standing = True
            self.bjoutput = self.name + doublemsg + " draws " + self.drawcard[0] + " and goes KAPOW Final hand: " + "".join(
                self.hand) + " (" + str(self.value) + ") " + choice(bjreactpos)

    def stand(self):
        self.standing = True
        self.bjoutput = self.name + " stands. Final hand: " + "".join(self.hand) + " (" + str(self.value) + ") Good luck " + choice(
            bjreactneg)


class Bjdealer:
    def __init__(self):
        self.drawcard = None
        self.hand = []
        self.value = 0
        self.aces = 0
        self.bust = False
        self.blackjack = False

        self.draw()

        # no premade message for the first card
        # dealer's messages are all created in a list at once. player's messages are created one string at a time
        self.bjoutput = []

        # the entire dealer hand is created at once from the start
        while self.value < 17:
            self.draw()

            if self.value < 17:
                self.bjoutput.append(choice(bjmsgdraw) + " " + self.drawcard[0] + ". My hand: " + "".join(self.hand) + " (" + str(
                    self.value) + ")")
            elif 17 <= self.value < 21:
                self.bjoutput.append(choice(bjmsgdraw) + " " + self.drawcard[0] + ". Final hand: " + "".join(self.hand) + " (" + str(
                    self.value) + ")")
            elif self.value == 21:
                if len(self.hand) == 2:
                    self.blackjack = True
                    self.bjoutput.append(
                        choice(bjmsgdraw) + " " + self.drawcard[0] + " which makes a Blackjack! Final hand: " + "".join(
                            self.hand) + " (BJ) " + choice(bjreactpos))
                else:
                    self.bjoutput.append(choice(bjmsgdraw) + " " + self.drawcard[0] + ". Final hand: " + "".join(
                        self.hand) + " (" + str(self.value) + ")")
            elif self.value > 21:
                self.bust = True
                self.bjoutput.append(choice(bjmsgdraw) + " " + self.drawcard[0] + " and KAPOW Final hand: " + "".join(
                    self.hand) + " (" + str(self.value) + ") " + choice(bjreactneg))

    def draw(self):
        self.drawcard = SystemRandom().choice(bjdeck)
        self.hand.append(self.drawcard[0])
        self.value += self.drawcard[1]
        if self.drawcard[1] == 11:
            self.aces += 1
        while self.aces > 0 and self.value > 21:
            self.aces -= 1
            self.value -= 10
