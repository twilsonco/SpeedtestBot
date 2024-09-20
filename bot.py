"""
Copyright © twilsonco 2022
Description: This is a discord bot to run an internet speedtest on your server

Version: 1.3
"""

import discord
import asyncio
import json
import subprocess
from discord.ext.commands import Bot
from discord.ext import commands
import os
import datetime
import pytz
import platform

# Load configuration from JSON file
config_path = '/config/config.json'

# Check if the config file exists
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

# Read and parse the JSON file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Set global variables from the config
REPORT_BITS = config.get('report_rate_in_bits', True)
BOT_PREFIX = config.get('bot_prefix', 's/')
TOKEN = config['bot_token']
OWNERS = config.get('bot_owners', [])
BLACKLIST = config.get('user_blacklist', [])
WHITELIST = config.get('user_whitelist', [])
CHANNEL_IDS = config.get('listen_for_commands_channel_ids', [])

# Set SPEEDTEST_TEST and SPEEDTEST_VERSION based on the speedtest_cli_path
SPEEDTEST_CLI_PATH = config.get('speedtest_cli_path', '/usr/bin/speedtest')
SPEEDTEST_TEST = [SPEEDTEST_CLI_PATH, '-f', 'json']
SPEEDTEST_VERSION = [SPEEDTEST_CLI_PATH, '--version']

intents = discord.Intents.default()

client = Bot(command_prefix=BOT_PREFIX, intents=intents)
LASTSPEEDTEST = None
LASTSPEEDTESTTIMESTAMP = None
LOCKED = False

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game("{}help".format(BOT_PREFIX)))
	print('Logged in as ' + client.user.name)
	print("Discord.py API version:", discord.__version__)
	print("Python version:", platform.python_version())
	print("Running on:", platform.system(), platform.release(), "(" + os.name + ")")
	print('-------------------')


def humanbytes(input_bytes, time_string='', report_bits=REPORT_BITS):
    'Return the given bits as a human friendly kB, MB, GB, or TB string'
    input_bytes = float(input_bytes) * (8 if report_bits else 1)
    unit = "b" if report_bits else "B"
    
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576 bytes or 8,388,608 bits
    GB = float(KB ** 3)  # 1,073,741,824 bytes or 8,589,934,592 bits
    TB = float(KB ** 4)  # 1,099,511,627,776 bytes or 8,796,093,022,208 bits

    if input_bytes < KB:
        out = '{0} '.format(input_bytes)
    elif KB <= input_bytes < MB:
        out = '{0:.2f} k'.format(input_bytes/KB)
    elif MB <= input_bytes < GB:
        out = '{0:.2f} M'.format(input_bytes/MB)
    elif GB <= input_bytes < TB:
        out = '{0:.2f} G'.format(input_bytes/GB)
    elif TB <= input_bytes:
        out = '{0:.2f} T'.format(input_bytes/TB)
    
    return out + unit + time_string

""" example speedtest result in json
{
    "type": "result",
    "timestamp": "2024-09-19T23:06:00Z",
    "ping": {
        "jitter": 0.41,
        "latency": 1.917,
        "low": 1.226,
        "high": 2.184
    },
    "download": {
        "bandwidth": 116895722,
        "bytes": 422161920,
        "elapsed": 3615,
        "latency": {
            "iqm": 7.609,
            "low": 1.421,
            "high": 12.798,
            "jitter": 0.708
        }
    },
    "upload": {
        "bandwidth": 115519302,
        "bytes": 726465682,
        "elapsed": 6309,
        "latency": {
            "iqm": 115.405,
            "low": 1.662,
            "high": 216.116,
            "jitter": 32.459
        }
    },
    "isp": "CenturyLink",
    "interface": {
        "internalIp": "172.20.0.13",
        "name": "eth0",
        "macAddr": "02:42:AC:14:00:0D",
        "isVpn": false,
        "externalIp": "184.96.240.66"
    },
    "server": {
        "id": 8862,
        "host": "denver.speedtest.centurylink.net",
        "port": 8080,
        "name": "CenturyLink",
        "location": "Denver, CO",
        "country": "United States",
        "ip": "63.224.243.196"
    },
    "result": {
        "id": "a2f5b224-4731-4ace-80c8-7d5b9ed6952e",
        "url": "https://www.speedtest.net/result/c/a2f5b224-4731-4ace-80c8-7d5b9ed6952e",
        "persisted": true
    }
}
"""
def st_to_embed(st, ts):
    embed = discord.Embed(title="Speedtest results (view online)", url=st["result"]["url"], color=0x53d6fd)
    
    embed.set_thumbnail(url="https://www.userlogos.org/files/logos/8596_famecky/st.png")
    
    time_unit_str = "ps" if REPORT_BITS else "/s"
    
    embed.add_field(name="⬇️ %s" % (humanbytes(st["download"]["bandwidth"], time_unit_str)), 
                    value="⬆️ %s" % (humanbytes(st["upload"]["bandwidth"], time_unit_str)), 
                    inline=True)
    
    embed.add_field(name="⚡️ %.2f ms Ping" % (st["ping"]["latency"]), 
                    value="〽️ %.2f ms Jitter" % (st["ping"]["jitter"]), 
                    inline=True)
    
    embed.set_footer(text="data used: %s down / %s up / %s total\n"
                          "server: %s\n"
                          "ISP: %s" % (
                              humanbytes(st["download"]["bytes"], report_bits=False),
                              humanbytes(st["upload"]["bytes"], report_bits=False),
                              humanbytes(st["download"]["bytes"] + st["upload"]["bytes"], report_bits=False),
                              f'{st["server"]["name"]} — {st["server"]["location"]}, {st["server"]["country"]} (id = {st["server"]["id"]})', 
                              st["isp"]
                          ))
    
    embed.timestamp = ts
    return embed

@client.command(name='last', pass_context=True)
async def lasttest(context):
	if len(CHANNEL_IDS) > 0 and context.message.channel.id not in CHANNEL_IDS:
		await context.message.channel.send("I don't respond to commands in this channel...")
		return False
	else:
		await context.message.channel.send('Showing results of last speedtest')
		st = LASTSPEEDTEST
		ts = LASTSPEEDTESTTIMESTAMP
		if st is not None and ts is not None:
			await context.message.channel.send(embed=st_to_embed(st,ts))
		else:
			await context.message.channel.send("No previous speedtest results to show...")

@client.command(name='test', pass_context=True)
async def test(context, *, content = ""):
	global LASTSPEEDTEST, LASTSPEEDTESTTIMESTAMP, LOCKED
	if LOCKED:
		return
	LOCKED = True
	if len(CHANNEL_IDS) > 0 and context.message.channel.id not in CHANNEL_IDS:
		await context.message.channel.send("I don't respond to commands in this channel...")
		return False
	elif context.message.author.id in BLACKLIST or (len(WHITELIST) > 0 and context.message.author.id not in WHITELIST) and LASTSPEEDTEST is not None:
		await lasttest(context)
	else:
		if content == "":
			await context.message.channel.send('Running speedtest on server (not on your local machine). Please wait...')
			async with context.channel.typing():
				st_raw = "no output: command not run"
				try:
					st_raw = subprocess.check_output(SPEEDTEST_TEST).decode()
					st = json.loads(st_raw)
					ts = datetime.datetime.now(tz=pytz.timezone('America/Denver'))
					LASTSPEEDTEST = st
					LASTSPEEDTESTTIMESTAMP = ts
					await context.message.channel.send(embed=st_to_embed(st,ts))
				except Exception as e:
					print(f"Error encountered during speedtest: {e}\n\nRaw output of speedtest utility:\n{st_raw}")
					await context.message.channel.send(f"Error encountered during speedtest: {e}\n\nRaw output of speedtest utility:\n{st_raw}")
		elif content == "info":
			testResult = subprocess.check_output(SPEEDTEST_VERSION)
			for l in testResult.decode().split('\n'):
				if len(l) > 0:
					await context.message.channel.send(l)
	LOCKED = False
				
client.remove_command('help')

@client.command(name='help', description='Help HUD.', brief='HELPOOOO!!!', pass_context=True)
async def help(context):
	if len(CHANNEL_IDS) > 0 and context.message.channel.id not in CHANNEL_IDS:
		await context.message.channel.send("I don't respond to commands in this channel...")
		return False
	elif context.message.author.id in BLACKLIST or (len(WHITELIST) > 0 and context.message.author.id not in WHITELIST) and LASTSPEEDTEST is not None:
		embed = discord.Embed(title='You\'re not allowed to run this!', description='Ask the owner to add you to the list.', color=0x53d6fd)
		await context.message.channel.send(embed=embed)
	else:
		embed = discord.Embed(title='Speedtest Bot', description='List of commands are:', color=0x53d6fd)
		embed.add_field(name='Speedtest - Run Speedtest on machine running bot and report results', value='Usage: `{}test [info]`'.format(BOT_PREFIX), inline=False)
		embed.add_field(name='Help - Gives this menu', value='Usage: `{}help`'.format(BOT_PREFIX), inline=False)
		await context.message.channel.send(embed=embed)

@client.event
async def on_command_error(context, error):
	if isinstance(error, commands.CommandOnCooldown):
		await context.message.delete()
		embed = discord.Embed(title="Error!", description='This command is on a %.2fs cooldown' % error.retry_after, color=0x53d6fd)
		message = await context.message.channel.send(embed=embed)
		await asyncio.sleep(5)
		await message.delete()
	elif isinstance(error, commands.CommandNotFound):
		await context.message.delete()
		embed = discord.Embed(title="Error!", description="I don't know that command!", color=0x53d6fd)
		message = await context.message.channel.send(embed=embed)
		await asyncio.sleep(2)
		await help(context)
	raise error

client.run(TOKEN)
