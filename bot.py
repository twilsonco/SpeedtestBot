"""
Copyright © twilsonco 2020
Description: This is a discord bot to run an internet speedtest on your server

Version: 1.2
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
SPEEDTEST_PATH='/usr/local/bin/speedtest'


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


def humanbytes(B):
	'Return the given bytes as a human friendly KB, MB, GB, or TB string'
	B = float(B)
	KB = float(1024)
	MB = float(KB ** 2) # 1,048,576
	GB = float(KB ** 3) # 1,073,741,824
	TB = float(KB ** 4) # 1,099,511,627,776

	if B < KB:
		return '{0} {1}'.format(B,'B')
	elif KB <= B < MB:
		return '{0:.2f} kB'.format(B/KB)
	elif MB <= B < GB:
		return '{0:.2f} MB'.format(B/MB)
	elif GB <= B < TB:
		return '{0:.2f} GB'.format(B/GB)
	elif TB <= B:
		return '{0:.2f} TB'.format(B/TB)
	  
def tobytes(B):
	'Return the number of bytes given by a string (a float followed by a space and the unit of prefix-bytes eg. "21.34 GB")'
	numstr = B.lower().split(' ')
	KB = (('kilo','kb','kb/s'),float(1024))
	MB = (('mega','mb','mb/s'),float(KB[1] ** 2)) # 1,048,576
	GB = (('giga','gb','gb/s'),float(KB[1] ** 3)) # 1,073,741,824
	TB = (('tera','tb','tb/s'),float(KB[1] ** 4)) # 1,099,511,627,776
	
	for prefix in (KB,MB,GB,TB):
		if numstr[1] in prefix[0]:
			return float(float(numstr[0]) * prefix[1])

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
		await context.message.channel.send('Showing results of last speedtest')
		st = LASTSPEEDTEST
		ts = LASTSPEEDTESTTIMESTAMP
	else:
		if content == "":
			await context.message.channel.send('Running speedtest on server (not on your local machine). Please wait...')
			st = subprocess.check_output([SPEEDTEST_PATH]).decode()
			ts = datetime.datetime.now(tz=pytz.timezone('America/Denver'))
			LASTSPEEDTEST = st
			LASTSPEEDTESTTIMESTAMP = ts
			stinfo = {i[0]:re.search(i[1],st) for i in [
				['server','Server:\s*(.*)\n'],
				['isp','ISP:\s*(.*)\n'],
				['lat','Latency:\s*([0-9\.]+)\s*(.*?)\s*\(([0-9\.]+)\s*([a-z]+)\s*?.*?\)'],
				['down','Download:\s*([0-9\.]+)\s*(.*?)\s*\(.*?:\s*?([0-9\.]+ .*?)\s*?\)'],
				['up','Upload:\s*([0-9\.]+)\s*(.*?)\s*\(.*?:\s*?([0-9\.]+.*?)\s*?\)'],
				['pack','Packet Loss:\s*(.+)\n'],
				['url','Result URL:\s*(.*)']
			]}
			if None not in stinfo.values():
				embed=discord.Embed(title="Speedtest results (view online)", url=stinfo['url'].group(1), color=0x53d6fd)
				embed.set_thumbnail(url="https://www.userlogos.org/files/logos/8596_famecky/st.png")
				embed.add_field(name="⬇️ %s %s" % (stinfo['down'].group(1),stinfo['down'].group(2)), value="⬆️ %s %s" % (stinfo['up'].group(1),stinfo['up'].group(2)), inline=True)
				embed.add_field(name="⚡️ %s %s Ping" % (stinfo['lat'].group(1),stinfo['lat'].group(2)), value="〽️ %s %s Jitter" % (stinfo['lat'].group(3),stinfo['lat'].group(4)), inline=True)
				embed.set_footer(text="packet loss: %s\ndata used: %s down / %s up / %s total\nserver: %s\nISP: %s" % (stinfo['pack'].group(1), 
				stinfo['down'].group(3),
				stinfo['up'].group(3),
				humanbytes(tobytes(stinfo['down'].group(3))+tobytes(stinfo['up'].group(3))),
				stinfo['server'].group(1), 
				stinfo['isp'].group(1)))
				embed.timestamp = ts
				await context.message.channel.send(embed=embed)
			else:
				await context.message.channel.send(st)
		elif content == "info":
			testResult = subprocess.check_output([SPEEDTEST_PATH,'--version'])
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
