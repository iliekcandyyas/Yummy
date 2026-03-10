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
from flask import Flask
from threading import Thread
from groq import Groq


ENV_FILE = Path(__file__).resolve().parent / ".env"


load_dotenv()  # loads .env locally if it exists, ignored on Railway

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768").strip()

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN not set — add it to Railway Variables")

import requests


token = DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Add this line
bot = commands.Bot(command_prefix='Clanker ', intents=intents)
groq_client = Groq(api_key=GROQ_API_KEY)
import time
bot.launch_time = time.time()

ALLOWED_CHANNEL_IDS = None

conversation_histories = {}

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced globally.")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")
    print(f'Logged in as {bot.user}')


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
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()


    if message.author.id == 1348737415765954726 or message.author.id == 1304112685599690863:
        await message.channel.send(f"Please fuck off — willingly")
    # ---- Auto-reactions ----
    if message.author.id == 1346416667466399746 or message.author.id == 1304112685599690863 or message.author.id == 1236143124481310764:
        try:
            await message.add_reaction("💗")
        except (discord.Forbidden, discord.HTTPException):
            pass

    # ---- Keyword responses ----
    if "good girl" in content:
        if message.author.id == 1236143124481310764:
            await message.channel.send("thank you daddy!")
            await message.add_reaction("❤️")
        else:
            await message.channel.send("Sybau nigga!")


    if "kys" in content:
        await message.channel.send("No promoting self harm. ~~Only I can promote it~~")

    if "bitch" in content:
        await message.channel.send("tsk tsk")

    # ---- Chatbot ----
    user_message = None

    if bot.user in message.mentions:
        user_message = message.content.replace(f"<@{bot.user.id}>", "").strip()
    elif message.content.startswith("Yummy, "):
        user_message = message.content[len("Yummy, "):].strip()

    if user_message is not None:
        if not user_message:
            await message.channel.send("Hey! Ask me anything.")
        else:
            user_id = message.author.id
            if user_id not in conversation_histories:
                conversation_histories[user_id] = []

            conversation_histories[user_id].append({"role": "user", "content": user_message})
            conversation_histories[user_id] = conversation_histories[user_id][-20:]

            async with message.channel.typing():
                try:
                    response = groq_client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant in a Discord server. Be concise and friendly."},
                            *conversation_histories[user_id]
                        ],
                        max_tokens=1000
                    )
                    reply = response.choices[0].message.content
                    conversation_histories[user_id].append({"role": "assistant", "content": reply})

                    if len(reply) > 2000:
                        for i in range(0, len(reply), 2000):
                            await message.channel.send(reply[i:i+2000])
                    else:
                        await message.reply(reply)
                except Exception as e:
                    await message.channel.send(f"⚠️ Error: {str(e)}")

    await bot.process_commands(message)

# --- Commands ---
@bot.command(name="clear")
async def clear_history(ctx):
    conversation_histories.pop(ctx.author.id, None)
    await ctx.send("✅ Conversation history cleared.")

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

@bot.command()
async def ateeb(ctx):
    await ctx.send("Ateeb is a big nigger!<3")

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

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.calculator")
    await bot.load_extension("cogs.graph_command")
    await bot.load_extension("cogs.slash_commands")
        
bot.run(token)






