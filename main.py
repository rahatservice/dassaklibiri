import os
import random
import discord

from collections import defaultdict
from discord.ext import commands
from discord.ui import View, Select

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

# =========================
# DATABASE
# =========================

oyuncu_deger = defaultdict(lambda: 1)
kayit_sayilari = defaultdict(int)
antrenman = defaultdict(int)

warnings = {}

# LIG
lig_adi = None
lig_takimlari = []
fikstur = []

puan = defaultdict(lambda: {
    "p":0,"g":0,"b":0,"m":0
})

# =========================
# IDS
# =========================

KAYIT_YETKILI = 1503341765178953739
DEGER_YETKILI = 1503341767049740369
ANTRENMAN_KANAL = 1503342068821655653

# =========================
# READY
# =========================

@bot.event
async def on_ready():
    print("Bot aktif")

# =========================
# ANTRENMAN
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id == ANTRENMAN_KANAL:

        antrenman[message.author.id] += 1

        s = antrenman[message.author.id]

        if s < 5:

            await message.channel.send(
                f"🏋️ {s}/5 antrenman"
            )

        else:

            antrenman[message.author.id] = 0
            oyuncu_deger[message.author.id] += 3

            await message.channel.send(
                f"🔥 +3M verildi"
            )

    await bot.process_commands(message)

# =========================
# KAYIT
# =========================

@bot.command()
@commands.has_role(KAYIT_YETKILI)
async def k(ctx, member: discord.Member, *, isim):

    await member.edit(nick=isim)

    oyuncu_deger[member.id] = 1

    await ctx.send(
        f"📋 {member.mention} → {isim}"
    )

# =========================
# DEGER
# =========================

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dver(ctx, member: discord.Member, amount=None):

    if amount is None:

        return await ctx.send(
            "❌ Kullanım: `.dver @kullanıcı 3`"
        )

    if not str(amount).isdigit():

        return await ctx.send(
            "❌ Sadece sayı yaz"
        )

    amount = int(amount)

    oyuncu_deger[member.id] += amount

    await ctx.send(
        f"💰 +{amount}M → {oyuncu_deger[member.id]}M"
    )

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dsil(ctx, member: discord.Member, amount: int):

    oyuncu_deger[member.id] = max(
        1,
        oyuncu_deger[member.id] - amount
    )

    await ctx.send(
        f"📉 {oyuncu_deger[member.id]}M"
    )

@bot.command()
async def dsayi(ctx, member: discord.Member=None):

    member = member or ctx.author

    await ctx.send(
        f"💰 {oyuncu_deger[member.id]}M"
    )

# =========================
# ARA
# =========================

@bot.command()
async def ara(ctx, *, isim):

    res = []

    for m in ctx.guild.members:

        n = m.nick or m.name

        if isim.lower() in n.lower():

            res.append(f"{m.mention} → {n}")

    if not res:
        return await ctx.send("Bulunamadı")

    await ctx.send("\n".join(res[:10]))

# =========================
# LIG
# =========================

@bot.command()
async def ligekle(ctx, *, isim):

    global lig_adi
    lig_adi = isim

    await ctx.send(f"🏆 Lig: {isim}")

@bot.command()
async def ligtakımekle(ctx):

    roles = ctx.message.role_mentions

    for r in roles:

        if r not in lig_takimlari:
            lig_takimlari.append(r)

    await ctx.send("Takımlar eklendi")

@bot.command()
async def fiksturolustur(ctx):

    global fikstur
    fikstur = []

    hafta = 1

    for i in range(len(lig_takimlari)):

        for j in range(i+1, len(lig_takimlari)):

            fikstur.append({
                "h": hafta,
                "ev": lig_takimlari[i],
                "dep": lig_takimlari[j],
                "s1": random.randint(0,5),
                "s2": random.randint(0,5)
            })

            hafta += 1

    await ctx.send("Fikstür hazır")

@bot.command()
async def hafta(ctx, no: int):

    m = [x for x in fikstur if x["h"] == no]

    if not m:
        return await ctx.send("Yok")

    txt = ""

    for x in m:

        txt += (
            f"{x['ev'].mention} "
            f"{x['s1']}-{x['s2']} "
            f"{x['dep'].mention}\n"
        )

    await ctx.send(txt)

@bot.command()
async def puan(ctx):

    s = sorted(
        puan.items(),
        key=lambda x: x[1]["p"],
        reverse=True
    )

    txt = ""

    for i,(id,v) in enumerate(s,1):

        r = ctx.guild.get_role(id)

        txt += f"{i}. {r.mention} {v['p']}p\n"

    await ctx.send(txt)

# =========================
# HELP
# =========================

@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="⚽ BOT MENÜ",
        description="""
.k
.dver
.dsil
.dsayi
.ligekle
.fiksturolustur
.ara
        """,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

# =========================
# RUN
# =========================

bot.run(TOKEN)
