# Speedtest Discord Bot
A python Discord bot for running an internet speedtest on the machine running the bot using the [Speedtest CLI](https://www.speedtest.net/apps/cli).
This bot is adapted from [kkrypt0nn's bot template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template).

## Features
* Simple setup: point to Speedtest CLI, make bot and run `s/test` to run speedtest and report results
* Control which users can run and on which channels (unauthorized users are presented with the results of the most recent speedtest)
* Pretty output using embeds
* Example output:

## Example image
![ex](https://github.com/twilsonco/SpeedtestBot/blob/master/ex-results.png)

## Install
1. Get [Speedtest CLI](https://www.speedtest.net/apps/cli).
2. Install python 3
3. Clone this repository using `git clone https://github.com/twilsonco/SpeedtestBot`

## Configure
1. Setup your new bot on Discord:
	1. Sign up for a Discord [developer account](https://discord.com/developers/docs)
	2. Go to the [developer portal](https://discordapp.com/developers/applications), click *New Application*, pick a name and click *Create*
		* *Note the `CLIENT ID`*
	3. Click on *Bot* under *SETTINGS* and then click *Add Bot*
	4. Fill out information for the bot and **uncheck the `PUBLIC BOT` toggle**
		* *Note the bot `TOKEN`*
2. Invite the bot to your server
	1. Go to `https://discordapp.com/api/oauth2/authorize?client_id=<client_id>&scope=bot&permissions=<permissions>`
		* replace `<client_id>` with the `CLIENT ID` from above
		* replace `<permissions>` with the minimum permissions `26624`(*for send messages, manage messages, embed links*) or administrator permissions `8` to keep things simple
	2. Invite the bot to your server
2. Configure `bot.py`
	1. Set discord options
		* `TOKEN` to your bot secret token
		* Lists of `OWNERS`, `BLACKLIST` and/or `WHITELIST` users, and `CHANNEL_IDS` on which the bot should listen for commands
			* get these ids by [enabling developer mode in your Discord client](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) and right-clicking on a user/channel
		* Pick a `BOT_PREFIX` (default is `s/`)
	2. Set Speedtest CLI information
		* `SPEEDTEST_PATH` points to the Speedtest CLI executable
3. Run with `python3 /path/to/SpeedtestBot/bot.py` and enjoy!

## To-do
* I think that's it...

## Author(s)

* Tim Wilson

## Thanks to:

* kkrypt0nn

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
