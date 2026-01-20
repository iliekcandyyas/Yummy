import discord
import os
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import commands
from numpy import *
import numexpr
import aiohttp
from discord.ext import commands
import asyncio
from discord import ui, ButtonStyle, Embed






ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


load_dotenv(dotenv_path=ENV_FILE)

FAL_KEY = (os.getenv("FAL_KEY") or "").strip()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FAL_KEY = (os.getenv("FAL_KEY") or "").strip()



if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN not found in .env")

if not FAL_KEY:
    print("⚠️ Fal.ai API key missing")

import requests


token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Add this line
bot = commands.Bot(command_prefix='^', intents=intents)
import time
bot.launch_time = time.time()

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced globally.")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(1456624421744672834)
    await channel.send('>.<')

@bot.command()
async def wassup(ctx):
    await ctx.send('wassup my nga!')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f'{member} became a certified gooner on {member.joined_at}')

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

@bot.command()
async def members(ctx):
    await ctx.send(f'This cult has {ctx.guild.member_count} gooners!!')

@bot.event
async def on_message(message: discord.Message):
    # ignore the bot's own messages to avoid loops
    if message.author.id == bot.user.id:
        return

    # check if the message is from the target user
    if message.author.id == 1346416667466399746:
        try:
            await message.add_reaction("💗")
        except discord.Forbidden:
            print("Missing permission to add reactions.")
        except discord.HTTPException:
            print("Failed to add reaction.")
    elif message.author.id == 1304112685599690863:
        try:
            await message.add_reaction("💗")
        except discord.Forbidden:
            print("Missing permission to add reactions.")
        except discord.HTTPException:
            print("Failed to add reaction.")
    
    await bot.process_commands(message)

@bot.command(name="testheart")
async def testheart(ctx):
    try:
        await ctx.message.add_reaction("💗")  # pink heart
    except discord.Forbidden:
        await ctx.send("I don’t have permission to add reactions here.")
    except discord.HTTPException:
        await ctx.send("Failed to add the reaction.")

@bot.command()
async def roll(ctx, sides: int = 6):
    import random
    await ctx.send(f'🎲 You rolled: {random.randint(1, sides)}')

@bot.command()
async def userid(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f'{member} = {member.id}')

@bot.command()
async def coinflip(ctx):
    import random
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'🪙 {result}!')

@bot.command()
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f'yeeted {member}')

@bot.command()
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f'erased {member}')

@bot.command()
async def say(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def echo(ctx, *, message: str):
    await ctx.send(message)

@bot.command()
async def search(ctx, *, query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await ctx.send(f"ugh.. you really cant do it yourselves? fine, here are the results for'{query}': {search_url}") 

@bot.command()
@commands.is_owner() # Optional: restricts the command to the bot owner
async def shutdown(ctx):
    await ctx.send("IM DYING HELP- *evaporates* womp.. womp..")
    await ctx.bot.close()
    
@bot.command()
@commands.is_owner()
async def uptime(ctx):
    import time
    current_time = time.time()
    uptime_seconds = int(current_time - bot.launch_time)

    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await ctx.send(f"Uptime: {hours}h {minutes}m {seconds}s")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "good girl":
        if message.author.id == 1236143124481310764:
            await message.channel.send("thank you daddy!")
            await message.add_reaction("❤️")
        else:
            await message.channel.send("Sybau nigga!")

    await bot.process_commands(message)


@bot.command()
async def sync(ctx):
    if await bot.is_owner(ctx.author): # Optional: make it owner-only
        await bot.tree.sync() # Syncs global commands
        await ctx.send("Commands synced globally!")
    else:
        await ctx.send("You must be daddy to use this command.")


@bot.command()
async def cats(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.thecatapi.com/v1/images/search") as r:
            data = await r.json()

    await ctx.send(data["message"])

import asyncio

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.calculator")
    await bot.load_extension("cogs.graph_command")
    await bot.load_extension("cogs.slash_commands")
        
bot.run(token)