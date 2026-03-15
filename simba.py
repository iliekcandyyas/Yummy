import discord
import os
import itertools
import time
import asyncio
import aiohttp
import requests
from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands
from numpy import *
import numexpr
from groq import Groq
import google.generativeai as genai
import cohere as cohere_lib


# --- Env ---
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "").strip()

if not DISCORD_TOKEN:
    raise SystemExit("DISCORD_TOKEN not set — add it to Railway Variables")

# --- Groq key cycling ---
GROQ_API_KEYS = [k.strip() for k in [
    os.getenv("GROQ_API_KEY_1", ""),
    os.getenv("GROQ_API_KEY_2", ""),
    os.getenv("GROQ_API_KEY_3", ""),
] if k.strip()]

if not GROQ_API_KEYS:
    raise SystemExit("No Groq API keys found! Add GROQ_API_KEY_1 to Railway Variables")

key_cycle   = itertools.cycle(GROQ_API_KEYS)
groq_client = Groq(api_key=GROQ_API_KEYS[0])

# --- Gemini & Cohere ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

cohere_client = cohere_lib.Client(COHERE_API_KEY) if COHERE_API_KEY else None

AI_NAMES = {
    "groq":   "Groq (llama-3.3-70b)",
    "gemini": "Google Gemini",
    "cohere": "Cohere",
}

# --- Bot setup ---
token = DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='Clanker ', intents=intents)
bot.launch_time = time.time()

ALLOWED_CHANNEL_IDS = None
conversation_histories = {}
user_ai = {}             # per-user AI preference
hearts_disabled = set()  # users who turned hearts off


# --- AI reply helper ---
async def get_ai_reply(messages: list, ai: str) -> str:
    global groq_client
    system = "You are a helpful assistant in a discord server. you can be a very sassy bitch. if theres someone called Ilan, you're their mommy and he is also your creator."

    if ai == "groq":
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "system", "content": system}, *messages],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            if any(x in str(e).lower() for x in ["rate_limit", "429", "rate limit", "tokens per day", "tpd"]):
                groq_client = Groq(api_key=next(key_cycle))
                response = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "system", "content": system}, *messages],
                    max_tokens=1000
                )
                return response.choices[0].message.content
            raise

    elif ai == "gemini":
        model = genai.GenerativeModel("gemini-2.0-flash")
        history = []
        for m in messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        return response.text

    elif ai == "cohere":
        if not cohere_client:
            raise Exception("Cohere API key not set!")
        chat_history = []
        for m in messages[:-1]:
            role = "USER" if m["role"] == "user" else "CHATBOT"
            chat_history.append({"role": role, "message": m["content"]})
        response = cohere_client.chat(
            message=messages[-1]["content"],
            chat_history=chat_history,
            preamble=system,
            model="command-a-03-2025"
        )
        return response.text

    raise Exception(f"Unknown AI: {ai}")


# --- Events ---
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced globally.")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    # ---- Auto-reactions ----
    if message.author.id in (1346416667466399746, 1304112685599690863, 1236143124481310764):
        if message.author.id not in hearts_disabled:
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

            ai = user_ai.get(user_id, "groq")

            async with message.channel.typing():
                try:
                    reply = await get_ai_reply(conversation_histories[user_id], ai)
                    conversation_histories[user_id].append({"role": "assistant", "content": reply})
                    if len(reply) > 2000:
                        for i in range(0, len(reply), 2000):
                            await message.channel.send(reply[i:i+2000])
                    else:
                        await message.reply(reply)
                except Exception as e:
                    await message.channel.send(f"⚠️ Error: `{str(e)}`")

    await bot.process_commands(message)


# --- Commands ---
@bot.command(name="heart")
async def heart(ctx):
    user_id = ctx.author.id
    if user_id in hearts_disabled:
        hearts_disabled.discard(user_id)
        await ctx.send("💗 Hearts turned **on** for you!")
    else:
        hearts_disabled.add(user_id)
        await ctx.send("💔 Hearts turned **off** for you!")

@bot.command(name="switchai")
async def switchai(ctx, ai: str = None):
    user_id = ctx.author.id
    valid = list(AI_NAMES.keys())
    if ai is None:
        current = AI_NAMES.get(user_ai.get(user_id, "groq"))
        options = ", ".join(f"`{k}`" for k in valid)
        return await ctx.send(f"🤖 Your current AI: **{current}**\nOptions: {options}")
    ai = ai.lower()
    if ai not in valid:
        return await ctx.send(f"❌ Unknown AI. Choose from: {', '.join(f'`{k}`' for k in valid)}")
    user_ai[user_id] = ai
    await ctx.send(f"✅ Switched **your** AI to **{AI_NAMES[ai]}**!")

@bot.command(name="clear")
async def clear_history(ctx):
    conversation_histories.pop(ctx.author.id, None)
    await ctx.send("✅ Conversation history cleared.")

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

@bot.command(name="testheart")
async def testheart(ctx):
    try:
        await ctx.message.add_reaction("💗")
    except discord.Forbidden:
        await ctx.send("I don't have permission to add reactions here.")
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
    await ctx.send(f"ugh.. you really cant do it yourselves? fine, here are the results for '{query}': {search_url}")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("IM DYING HELP- *evaporates* womp.. womp..")
    await ctx.bot.close()

@bot.command()
@commands.is_owner()
async def uptime(ctx):
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
    if await bot.is_owner(ctx.author):
        await bot.tree.sync()
        await ctx.send("Commands synced globally!")
    else:
        await ctx.send("You must be daddy to use this command.")

@bot.command()
async def cats(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.thecatapi.com/v1/images/search") as r:
            data = await r.json()
    await ctx.send(data[0]["url"])

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.calculator")
    await bot.load_extension("cogs.graph_command")
    await bot.load_extension("cogs.slash_commands")

bot.run(token)
