# Speedtest Discord Bot
A python Discord bot for running an internet speedtest on the machine running the bot using the [Speedtest CLI](https://www.speedtest.net/apps/cli).
This bot is adapted from [kkrypt0nn's bot template](https://github.com/kkrypt0nn/Python-Discord-Bot-Template).

## Features
* Simple setup: point to Speedtest CLI, configure, make bot and run `s/test` to run speedtest and report results
  * Or use docker with the included Dockerfile (and docker-compose.yml)
* Control which users can run and on which channels (unauthorized users are presented with the results of the most recent speedtest)
* Pretty output using embeds
* Example output:

## Example image
![ex](https://github.com/twilsonco/SpeedtestBot/blob/master/ex-results.png?raw=true)

## Install without Docker
1. Get [Speedtest CLI](https://www.speedtest.net/apps/cli).
2. Run the following to accept the speedtest CLI license `speedtest --accept-license`
3. Install python 3
4. Clone this repository using `git clone https://github.com/twilsonco/SpeedtestBot`
5. Install dependencies using `pip install -r requirements.txt`

## Install with Docker
1. Install [Docker](https://docs.docker.com/get-docker/) on your system.
2. Clone this repository using `git clone https://github.com/twilsonco/SpeedtestBot`
3. Navigate to the cloned repository: `cd SpeedtestBot`

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
      * replace `<permissions>` with the minimum permissions `26624` (*for send messages, manage messages, embed links*) or administrator permissions `8` to keep things simple
   2. Invite the bot to your server

3. Configure the bot:
   1. Copy `config-sample.json` to `config/config.json`
   2. Edit `config/config.json` and set the following:
      * `bot_token`: Your bot secret token
      * `bot_owners`: List of owner user IDs
      * `user_blacklist` and/or `user_whitelist`: List of user IDs
      * `listen_for_commands_channel_ids`: List of channel IDs where the bot should listen for commands
      * `bot_prefix`: Set your desired prefix (default is `s/`)
   
   To get user and channel IDs, [enable developer mode in your Discord client](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) and right-click on a user/channel.

## Running the Bot

You can run the SpeedtestBot using either Docker commands or Docker Compose.

### Option 1: Using Docker Commands

Build the Docker image:
```bash
docker build -t speedtestbot .
```

Run the Docker container:
```bash
docker run -d --name speedtestbot -v $(pwd)/config:/config speedtestbot
```

### Option 2: Using Docker Compose

1. Create a `docker-compose.yml` file in your project root with the following content:
```yaml
version: '3'
services:
  speedtestbot:
    build: /path/to/workspace
    container_name: speedtestbot
    volumes:
      - ./config:/config
    restart: unless-stopped
```

2. Run the following command to start the bot:
```bash
docker-compose up -d
```

### Option 3: Running the Bot without Docker
Run with `python3 /path/to/SpeedtestBot/bot.py` and enjoy!

## To-do
* I think that's it...

## Author(s)

* Tim Wilson

## Thanks to:

* kkrypt0nn

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details
