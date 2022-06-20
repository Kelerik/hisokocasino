# hisokocasino

[![The Unlicense License Badge](https://img.shields.io/badge/license-The_Unlicense-blue)](https://choosealicense.com/licenses/unlicense/)

This chat bot is a personal project that I wrote for hisokeee, a friend of mine. It is an automated chat bot for his twitch.tv channel, written in Python.

- [hisokocasino](#hisokocasino)
- [Features](#features)
- [How to use](#how-to-use)
- [Bot Commands](#bot-commands)
  - [Master Commands](#master-commands)
  - [General Commands](#general-commands)
  - [Shared Cooldown Commands](#shared-cooldown-commands)

A few caveats:

-  It is currently hard-coded to connect to only his channel and from a his bot account.
-  Requires manually entering the authentication (oauth) key in a .txt file saved in the /data/ folder.
-  Requires Python to be installed in order to run. Optionally, a standalone .exe can be created using the included batch scripts (which themselves require Python).
-  Runs locally on your machine and saves data to your hard drive. No cloud backup or self-updating.
-  Consider this repository only as a source of inspiration. It was written solely by me, a self-taught python programmer who didn't quite learn ALL of the standard practices at the time. I still did my best to keep it DRY.

# Features

-  User activity tracking, pays currency to active chatters (this bot was made back in the day before Twitch introduced channel points as a native feature).
-  Includes "fun" games to spend that currency, such as slots, blackjack, roullette, and other miscellaneous betting games.
-  Many administrative commands to manage users (listed below).

# How to use

This bot was made with the intent of solely being used by hisokeee and his bot account. To connect to a different channel, and from a different account, the code must be modified. In `main.py`, the `irc_nick` sets the account name of the bot, and `irc_chan` sets the account name of the channel.

In the /data/ folder, create an `oauth.txt` file with the contents being the stream key of the bot account wrapped in quotes. Example: `"oauth:asdf1234asdf1234asdf1234asdf12"`

Run the `main.py` file (requires Python to be installed). Optionally, run the standalone .exe if it has been made.

Data is saved as JSON in the /data/ folder.

# Bot Commands

## Master Commands

    Masters (true masters only)
        !master add <name>
        !master remove <name

    Rename a user in all databases (NOTE: use their USERNAME, not DISPLAYNAME) (true masters only)
        !rename <oldname> <newname>

    Save data and restart (true masters only)
        !restart

    Save data and shut down (true masters only)
        !shutdown

    Change a user's gold to a certain number
        !(rare)gold set <user> <amount>

    Add gold
        !(rare)gold add <user> <amount>
        !(rare)gold add online <amount>
        !(rare)gold add all <amount>

    Subtract gold
        !(rare)gold remove <user> <amount>
        !(rare)gold remove online <amount>
        !(rare)gold remove all <amount>

    Delete a user and their gold from the database
        !(rare)gold delete <user> <amount>

    Gamble commands
        !gamble open <minbet> <maxbet> <payout> <choice1> <choice2> <choiceN> ...
        !gamble open <minbet> <maxbet> <payout>x <choice1> <choice2> <choiceN> ...
        !gamble winner <choice>
        !gamble close
        !gamble cancel

    Raffle commands
        !raffle open <payout> (rare)gold <keyword> <optional win message>
        !raffle draw
        !raffle reset
        !raffle close

    Slots enable/disable
        !slots on
        !slots off

    Blackjack commands
        !bj on
        !bj off
        !bj start
        !bj <user> <bet>
        !bj cancel

    Senpai commmands
        !senpai pay <name>
        !senpai pay all
        !senpai pay online
        !senpai draw
        !senpai draw <number>

    Hi Lo commands
        !hilo open <user> <rounds> <bet> <currency>
        !hilo cancel

    Vocaloid titles
        !vocaloid pay <name>

    Pets
        !pet list
        !pet draw
        !pet draw <number>

    Raids
        !raid start
        !raid on
        !raid off

    Roulette
        !roulette on <min> <max>
        !roulette off
        !roulette start <min> <max>

    Bot mute. All commands still work when muted, just no messages will be sent.
        !mute
        !unmute

## General Commands

    Check gold
        !(rare)gold
        !(rare)gold top5
        !(rare)gold <user>
        !casino

    Give raregold to another user
        !give <user> <amount>

    Convert gold to raregold (one way)
        !convert <amount>

    Gambling
        !bet <amount> <choice>
        !gamble help

    Lottery
        !lottery

    Slots
        !slots min
        !slots all
        !slots <amount>

        !slots stats
        !slots stats all
        !slots stats <user>

    Blackjack
        !bj <bet>
        hit
        stand
        stay
        double

        !bj stats
        !bj stats all
        !bj stats <user>

    Raffle
        !raffle info

    Senpai
        !roll senpai

        !senpai stats
        !senpai stats all
        !senpai stats <user>

    Roulette
        !roulette

        !roulette stats
        !roulette stats all
        !roulette stats <user>

    Vocaloid titles
        !roll <name>
        !vocaloid title <name>
        !vocaloid stats <name>

    Pets
        !roll pet

        !pet stats
        !pet stats all
        !pet stats <user>

        !pet rename <name>
        !pet level up

    Emote stats
        !<emote>
        !<emote <year>
        ! <emote>
        ! <emote <year>

## Shared Cooldown Commands

    !d<number>
    !calc <num><operation><num>
    !casino
    !bang <user>
    !hitman
    !weather
