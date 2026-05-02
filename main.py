import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

KANAL_ID = 1499363884593840149

user_counters = {}  # her kullanıcı için sayaç

@bot.event
async def on_ready():
    print(f"Bot aktif: {bot.user}")

@bot.command()
async def ant(ctx):
    user_id = ctx.author.id

    # yanlış kanal kontrolü
    if ctx.channel.id != KANAL_ID:
        kanal = bot.get_channel(KANAL_ID)

        embed = discord.Embed(
            title="❌ Yanlış Kanal",
            description=f"Bu komutu burada kullanamazsın.\nDoğru kanal: {kanal.mention}",
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)
        return

    # kullanıcı sayacı yoksa başlat
    if user_id not in user_counters:
        user_counters[user_id] = 0

    user_counters[user_id] += 1

    if user_counters[user_id] > 10:
        user_counters[user_id] = 1

    sayac = user_counters[user_id]

    embed = discord.Embed(
        title=f"⏳ {sayac}/10",
        description=f"{ctx.author.mention} için ilerleme devam ediyor...",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

bot.run("MTUwMDIyOTI2MTc1ODQzNTM4OA.Gc4xyw.KCrfwISjdmxcwIUBGvYrx3COTdfdp4QAZd7mCU")