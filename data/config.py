NOTIFIER_FREQUENCY = 60 * 15 # seconds

SQL_PATH = './data/proposals.db'

TG_BOT_API_TOKEN = 'insert_your_bot_api_token'
CHAT_ID = 1   # insert chat id, even if tarts with -
MESSAGE_THREAD_ID = 1 # insert MESSAGE_THREAD id

NOTIFIER_REMINDER_MODES = {
        "SOFT": (range(345_600, 3_036_800), 86_400),
        "MEDIUM": (range(172_800, 345_600), 43_200),
        "HARD": (range(86_400, 172_800), 21_600),
        "EXTREME": (range(0, 86_400), 1800)
}

NETWORKS = [
    {
        "name": "qwoyn",
        "lcd_api": "https://lcd.qwoyn-1.bronbro.io",
        "validator": "qwoynvaloper1dmfcpxnun5enhvx72cyvn5hcw3rjvnwd4u7r5f",
        "prefix": "qwoyn",
        "explorer": "https://cyb.ai/senate/"
    },
    {
        "name": "bostrom",
        "lcd_api": "https://lcd.bostrom.bronbro.io",
        "validator": "bostromvaloper1ydc5fy9fjdygvgw36u49yj39fr67pd9m5qexm8",
        "prefix": "bostrom",
        "explorer": "https://cyb.ai/senate/"
    },
    {
        "name": "osmosis",
        "lcd_api": "https://lcd.osmosis-1.bronbro.io",
        "validator": "osmovaloper13tk45jkxgf7w0nxquup3suwaz2tx483xe832ge",
        "prefix": "osmo",
        "explorer": "https://www.mintscan.io/osmosis/proposals/"
    },
    {
        "name": "juno",
        "lcd_api": "https://lcd.juno-1.bronbro.io",
        "validator": "junovaloper1quqxfrxkycr0uzt4yk0d57tcq3zk7srm7sm6r8",
        "prefix": "juno",
        "explorer": "https://www.mintscan.io/juno/proposals/"
    },
    {
        "name": "stargaze",
        "lcd_api": "https://lcd.stargaze-1.bronbro.io",
        "validator": "starsvaloper1y58hfnm90r4efhlydx0gavz57lvm7k6uulkg3h",
        "prefix": "stars",
        "explorer": "https://www.mintscan.io/stargaze/proposals/"
    },
    {
        "name": "gravity",
        "lcd_api": "https://lcd.gravity-bridge-3.bronbro.io",
        "validator": "gravityvaloper1vyd4k5j636erx5y5kdqghdu3rfjtwc48vdc7r6",
        "prefix": "gravity",
        "explorer": "https://www.mintscan.io/gravity-bridge/proposals/"
    },
    {
        "name": "evmos",
       "lcd_api": "https://lcd.evmos-9001-2.bronbro.io",
       "validator": "evmosvaloper1ce4vh0e5kanlgc7z0rhcemvd8erjnfzcyfecl7",
       "prefix": "evmos",
       "explorer": "https://www.mintscan.io/evmos/proposals/"
    },
    {
        "name": "crescent",
        "lcd_api": "https://lcd.crescent-1.bronbro.io",
        "validator": "crevaloper1c96vvme4k42zlvkc56fslmdpa2qj6u80xvqwau",
        "prefix": "cre",
        "explorer": "https://www.mintscan.io/crescent/proposals/"
    },
    {
        "name": "omniflix",
        "lcd_api": "https://lcd.omniflixhub-1.bronbro.io",
        "validator": "omniflixvaloper1e8grpphncncw9hrutyvnlv77n5dejwcne58zk4",
        "prefix": "omniflix",
        "explorer": "https://www.mintscan.io/omniflix/proposals/"
    },
    {
        "name": "cosmoshub",
        "lcd_api": "https://lcd.cosmoshub-4.bronbro.io",
        "validator": "cosmosvaloper106yp7zw35wftheyyv9f9pe69t8rteumjrx52jg",
        "prefix": "cosmos",
        "explorer": "https://www.mintscan.io/cosmos/proposals/"
    },
    {
        "name": "desmos",
        "lcd_api": "https://lcd.desmos-mainnet.bronbro.io",
        "validator": "desmosvaloper1sykf8q94l8q8mqstf64ptuvp74ueyehxpgcq76",
        "prefix": "desmos",
        "explorer": "https://www.mintscan.io/desmos/proposals/"
    },
    {
        "name": "stride",
        "lcd_api": "https://lcd.stride-1.bronbro.io",
        "validator": "stridevaloper1hl95uhecs4rwe0g432mknz2tsl84f0ltexpzc3",
        "prefix": "stride",
        "explorer": "https://www.mintscan.io/stride/proposals/"
    },
    {
        "name": "composable-finance",
        "lcd_api": "https://lcd.centauri-1.bronbro.io",
        "validator": "centaurivaloper19klmacamxh9cnmq209zxagnjzr5gw9ee9nwqnj",
        "prefix": "centauri",
        "explorer": "https://ping.pub/Centauri/gov"
    },
    {
        "name": "cosmic-horizon",
        "lcd_api": "https://lcd.qwoyn-1.bronbro.io",
        "validator": "qwoynvaloper1dmfcpxnun5enhvx72cyvn5hcw3rjvnwd4u7r5f",
        "prefix": "qwoun",
        "explorer": "https://ping.pub/qwoyn/gov"
    },
   {
       "name": "composable-finance",
       "lcd_api": "https://lcd.centauri-1.bronbro.io",
       "validator": "centaurivaloper19klmacamxh9cnmq209zxagnjzr5gw9ee9nwqnj",
       "prefix": "centauri",
       "explorer": "https://ping.pub/Centauri/gov/"
   },
]

PHRASES = {
        "SOFT": [
            'Hey 😀 Looks like its new proposal in the Cosmos ecosystem',
            'Take your time. But remember, you have to vote anyway! 😴',
            'Hello! Have a look to a new proposal! 😀',
            'Probably is there something interesting here? 🧐',
            'Yet another drama or not? 🤡',

        ],
        "MEDIUM": [
            'Tik-tok! The time has come! Your decision ❓',
            'I understand youre guys very busy 🥸🥸🥸, but one of the responsibilities of a validator is voting ‼️',
            'Just take a look on that, maybe is something interesting here...'
            'You havent voted yet? 😱😱😱'
        ],
        "HARD": [
            'Vote abstain if you have no idea 💩',
            'Yes? No? Abstain? No with veto? Hurry up, lets decide! 👊👊👊',
            'You have to vote. Please. 🤐',
            'There is no time for thinking! Decision! 👿'
        ],
        "EXTREME": [
            'You wanna die or what?',
            'I know a lot of irresponsible validators but you... 💩💩💩',
            'Wanna lose all of your delegators? You are close to.',
            'D E C I S I O N',
            'Hey 🤬. Get your butt up and vote!'
        ]
}
