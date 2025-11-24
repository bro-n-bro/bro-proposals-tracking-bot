# Telegram proposal tracker bot by your Bro

## What is this

This bot is designed to keep up validator governance activity on a decent level. It tracks upcoming and active proposals in every specified network and gently (sometimes not very:) reminds about the necessity to vote. 
We at Bro_n_Bro, have used this bot for a while now, and it helps to keep all governance happening in the front. It is targeted mainly at validators (and their teams) but also might be suitable for someone who likes to track specific validator governance activity.

## Setup

Firstly fill `config.py` inside `data/` folder. 

1. Insert telegram bot parameters (yes you'll need one to send reminders, use [BotFather](https://t.me/BotFather) to create it): 

```bash
TG_BOT_API_TOKEN = '123456789:jbd78sadvbdy63d37gda37bd8'
CHAT_ID = -122987163
```

2. Fill networks part. Rest api with http or https access required (it is the one that usually runs on 1317 port). Validators valoper address required.

**Single endpoint (simple):**
```python
    {
        "name": "osmosis",
        "lcd_api": "http://lcd.osmosis-1",
        "validator": "osmovaloper13tk45jkxgf7w0nxquup3suwaz2tx483xe832ge",
        "prefix": "osmo",
        "explorer": "https://www.mintscan.io/osmosis/proposals/"
    }
```

**Multiple endpoints with automatic fallback (recommended):**
```python
    {
        "name": "cosmos",
        "lcd_endpoints": [  # Use array instead of single string
            "https://rest.primary-provider.com/cosmoshub",
            "https://rest.backup-provider.com/cosmoshub",
            "https://rest.third-provider.com/cosmoshub"
        ],
        "validator": "cosmosvaloper1abc...",
        "prefix": "cosmos",
        "explorer": "https://www.mintscan.io/cosmos/proposals/"
    }
```
*If the first endpoint fails, the bot will automatically try the next one in the list.*

**Special chains:**
- **AtomOne**: requires `"gov_prefix": "atomone"` (uses `/atomone/gov/` instead of `/cosmos/gov/`)
- **Namada**: requires `"provider": "namada"` and `"indexers": [...]` array instead of lcd_api

It is possible to add or remove networks upon own requiremens\set of chains you need to monitor. 

3. Run the thing:

```bash
doker-compose up --detach .
```

Docker image should be built and lauched after. Track container logs to see if everyghing configured correctly. 

## Behavior 

The bot will track active proposals in every chain configured and will send notifications in case the configured validator hasn't voted for every active proposal. \
![](https://ipfs.io/ipfs/QmZ9E6LuuBfwbZDgs3bZKgtb18epQFEoNXotKBUfvBFSqj?filename=QmZ9E6LuuBfwbZDgs3bZKgtb18epQFEoNXotKBUfvBFSqj)

It is possible to adjust notifications timeframes and frequency in `config.py`. 

```bash
NOTIFIER_REMINDER_MODES = {
        "SOFT": (range(345_600, 3_036_800), 86_400)
```

The first time range defines how `soon` proposal will end, the last one is how often to send reminder. All numbers are in seconds so keep the formatting as it was in case of adjusting.

## Supported Networks

- **Standard Cosmos SDK chains** - Osmosis, Juno, Stargaze, Cosmos Hub, etc. (uses `gov v1beta1`)
- **Modern Cosmos SDK chains** - AtomOne, etc. (uses `gov v1` API with automatic fallback)
- **Namada** - Custom governance via Indexer API

The bot automatically detects which API version to use. For AtomOne and similar modern chains, add `"gov_version": "v1"` in config. 

Also, motivational phrases are located at the very bottom of `config.py`, which might be updated if needed.