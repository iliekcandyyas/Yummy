import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp
import time

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------- Fun Commands -----------------
    @app_commands.command(name="wassup", description="Say wassup")
    async def wassup(self, interaction: discord.Interaction):
        await interaction.response.send_message("wassup my nga!")

    @app_commands.command(name="hello", description="Say hello")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.name}!")

    @app_commands.command(name="ping", description="Check latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        await interaction.response.send_message(f"🎲 You rolled: {random.randint(1, sides)}")

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 {result}!")

    # ----------------- Info Commands -----------------
    @app_commands.command(name="userinfo", description="Get info about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(
            f"{member} became a certified gooner on {member.joined_at}"
        )

    @app_commands.command(name="avatar", description="Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(member.avatar.url)

    @app_commands.command(name="members", description="Get member count of the server")
    async def members(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"This cult has {interaction.guild.member_count} gooners!!")

    @app_commands.command(name="userid", description="Get a user's ID")
    async def userid(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        await interaction.response.send_message(f"{member} = {member.id}")

    # ----------------- Moderation Commands -----------------
    @app_commands.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await member.kick()
        await interaction.response.send_message(f"yeeted {member}")

    @app_commands.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await member.ban()
        await interaction.response.send_message(f"erased {member}")

    # ----------------- Messaging Commands -----------------
    @app_commands.command(name="say", description="Make the bot say something")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

    # ----------------- API / Random -----------------
    @app_commands.command(name="cats", description="Get a random cat image")
    async def cats(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as r:
                data = await r.json()
        await interaction.response.send_message(data[0]["url"])

    @app_commands.command(name="search", description="Search Google for something")
    async def search(self, interaction: discord.Interaction, query: str):
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await interaction.response.send_message(
            f"ugh.. you really cant do it yourselves? fine, here are the results for '{query}': {search_url}"
        )

    # ----------------- Owner Commands -----------------
    @app_commands.command(name="shutdown", description="Shut down the bot (owner only)")
    async def shutdown(self, interaction: discord.Interaction):
        if await self.bot.is_owner(interaction.user):
            await interaction.response.send_message("IM DYING HELP- *evaporates* womp.. womp..")
            await self.bot.close()
        else:
            await interaction.response.send_message("You must be daddy to use this command.", ephemeral=True)

    @app_commands.command(name="uptime", description="Check bot uptime (owner only)")
    async def uptime(self, interaction: discord.Interaction):
        if await self.bot.is_owner(interaction.user):
            uptime_seconds = int(time.time() - self.bot.launch_time)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(f"Uptime: {hours}h {minutes}m {seconds}s")
        else:
            await interaction.response.send_message("You must be daddy to use this command.", ephemeral=True)

    @app_commands.command(name="sync", description="Sync global slash commands (owner only)")
    async def sync(self, interaction: discord.Interaction):
        if await self.bot.is_owner(interaction.user):
            await self.bot.tree.sync()
            await interaction.response.send_message("Commands synced globally!")
        else:
            await interaction.response.send_message("You must be daddy to use this command.", ephemeral=True)

    # ----------------- Custom Reactions -----------------
    @app_commands.command(name="testheart", description="Add a pink heart reaction to your message")
    async def testheart(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("💗")  # placeholder since slash commands can't react to past messages
        except discord.Forbidden:
            await interaction.response.send_message("I don’t have permission to add reactions here.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
