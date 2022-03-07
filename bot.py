"""
Copyright © twilsonco 2022
Description: This is a discord bot to run an internet speedtest on your server

Version: 1.3
"""

import discord
import asyncio
import aiohttp
import json
import subprocess
from discord.ext.commands import Bot
from random import randint
from discord.ext import commands
from platform import python_version
import os
import re
import datetime
import pytz
import platform

BOT_PREFIX = 's/'
TOKEN = 'SECRET_TOKEN'
OWNERS = [OWNER_USER_IDS]
BLACKLIST = [USER_IDS]
WHITELIST = [USER_IDS]
CHANNEL_IDS=[CHANNEL_IDS]
SPEEDTEST_TEST=['/usr/local/bin/speedtest','-f','json']
SPEEDTEST_VERSION=['/usr/local/bin/speedtest','--version']


client = Bot(command_prefix=BOT_PREFIX)
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


def humanbytes(B, time_string=''):
	'Return the given bytes as a human friendly KB, MB, GB, or TB string'
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776

	if B < KB:
		return '{0} B'.format(B) + time_string
	elif KB <= B < MB:
		return '{0:.2f} kB'.format(B/KB) + time_string
	elif MB <= B < GB:
		return '{0:.2f} MB'.format(B/MB) + time_string
	elif GB <= B < TB:
		return '{0:.2f} GB'.format(B/GB) + time_string
	elif TB <= B:
		return '{0:.2f} TB'.format(B/TB) + time_string

""" example speedtest result in json
		{
		    "type": "result",
		    "timestamp": "2022-03-07T17:15:19Z",
		    "ping": {
		        "jitter": 0.81399999999999995,
		        "latency": 2.3500000000000001
		    },
		    "download": {
		        "bandwidth": 116707935,
		        "bytes": 676104480,
		        "elapsed": 5807
		    },
		    "upload": {
		        "bandwidth": 113990420,
		        "bytes": 1226035930,
		        "elapsed": 12005
		    },
		    "packetLoss": 0,
		    "isp": "CenturyLink",
		    "interface": {
		        "internalIp": "10.0.1.70",
		        "name": "en0",
		        "macAddr": "A8:20:66:45:B9:D8",
		        "isVpn": false,
		        "externalIp": "97.118.183.106"
		    },
		    "server": {
		        "id": 8862,
		        "name": "CenturyLink",
		        "location": "Denver, CO",
		        "country": "United States",
		        "host": "denver.speedtest.centurylink.net",
		        "port": 8080,
		        "ip": "205.171.253.6"
		    },
		    "result": {
		        "id": "bdb855ba-9533-4f60-b561-a6573f0e2831",
		        "url": "https://www.speedtest.net/result/c/bdb855ba-9533-4f60-b561-a6573f0e2831"
		    }
		}
"""
def st_to_embed(st,ts):
	embed=discord.Embed(title="Speedtest results (view online)", url=st["result"]["url"], color=0x53d6fd)
	
	embed.set_thumbnail(url="https://www.userlogos.org/files/logos/8596_famecky/st.png")
	
	embed.add_field(name="⬇️ %s" % (humanbytes(st["download"]["bandwidth"],'/s')), value="⬆️ %s" % (humanbytes(st["upload"]["bandwidth"],'/s')), inline=True)
	
	embed.add_field(name="⚡️ %.2f ms Ping" % (st["ping"]["latency"]), value="〽️ %.2f ms Jitter" % (st["ping"]["jitter"]), inline=True)
	
	embed.set_footer(text="packet loss: %.2f%%\ndata used: %s down / %s up / %s total\nserver: %s\nISP: %s" % (st["packetLoss"], 
	humanbytes(st["download"]["bytes"]),
	humanbytes(st["upload"]["bytes"]),
	humanbytes(st["download"]["bytes"]+st["upload"]["bytes"]),
	f'{st["server"]["name"]} — {st["server"]["location"]}, {st["server"]["country"]} (id = {st["server"]["id"]})', 
	st["isp"]))
	
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
				st = json.loads(subprocess.check_output(SPEEDTEST_TEST).decode())
				ts = datetime.datetime.now(tz=pytz.timezone('America/Denver'))
				LASTSPEEDTEST = st
				LASTSPEEDTESTTIMESTAMP = ts
				await context.message.channel.send(embed=st_to_embed(st,ts))
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
