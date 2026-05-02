import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

KANAL_ID = 1499363884593840149

user_counters = {}

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

@bot.command()
async def ant(ctx):
    user_id = ctx.author.id

    if ctx.channel.id != KANAL_ID:
        kanal = await bot.fetch_channel(KANAL_ID)

        embed = discord.Embed(
            title="❌ Yanlış Kanal",
            description=f"Burada olmaz.\nDoğru kanal: {kanal.mention}",
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)
        return

    user_counters[user_id] = user_counters.get(user_id, 0) + 1

    if user_counters[user_id] > 10:
        user_counters[user_id] = 1

    embed = discord.Embed(
        title=f"⏳ {user_counters[user_id]}/10",
        description=f"{ctx.author.mention} ilerliyorsun… sabır (maalesef)",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

bot.run(os.getenv("TOKEN"))
