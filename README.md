# hisokocasino
 
MASTER COMMANDS :
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


GENERAL COMMANDS:
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


SHARED COOLDOWN COMMANDS:
    !d<number>
    !calc <num><operation><num>
    !casino
    !bang <user>
    !hitman
    !weather
