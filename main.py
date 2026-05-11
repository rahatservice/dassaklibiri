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
kayit_sayisi = defaultdict(int)
antrenman = defaultdict(int)

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
                f"🏋️ {message.author.mention} {s}/5 antrenman"
            )

        else:

            antrenman[message.author.id] = 0
            oyuncu_deger[message.author.id] += 3

            await message.channel.send(
                f"🔥 {message.author.mention} +3M kazandı"
            )

    await bot.process_commands(message)

# =========================
# KAYIT (.k)
# =========================

@bot.command()
@commands.has_role(KAYIT_YETKILI)
async def k(ctx, member: discord.Member, *, veri):

    try:

        # format: isim | 1M | 🇪🇸 | SĞK
        p = [x.strip() for x in veri.split("|")]

        if len(p) != 4:
            return await ctx.send(
                "❌ Format: `isim | 1M | ülke | mevki`"
            )

        isim, deger, ulke, mevki = p

        oyuncu_deger[member.id] = int(
            deger.upper().replace("M","")
        )

        await member.edit(
            nick=f"{isim} | {deger} | {ulke} | {mevki}"
        )

        kayit_sayisi[ctx.author.id] += 1

        await ctx.send(
            f"📋 {member.mention} kayıt edildi"
        )

    except:

        await ctx.send(
            "❌ Hata oluştu"
        )

# =========================
# DEGER (.dver)
# =========================

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dver(ctx, member: discord.Member, amount=None):

    if amount is None:

        return await ctx.send(
            f"❌ Kullanım: `.dver {member.mention} 3`"
        )

    if not str(amount).isdigit():

        return await ctx.send(
            "❌ Sadece sayı yaz"
        )

    amount = int(amount)

    oyuncu_deger[member.id] += amount

    await ctx.send(
        f"💰 {member.mention} +{amount}M → "
        f"{oyuncu_deger[member.id]}M"
    )

# =========================
# DEGER AZALT
# =========================

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dsil(ctx, member: discord.Member, amount: int):

    oyuncu_deger[member.id] = max(
        1,
        oyuncu_deger[member.id] - amount
    )

    await ctx.send(
        f"📉 {member.mention} → "
        f"{oyuncu_deger[member.id]}M"
    )

# =========================
# GOSTER
# =========================

@bot.command()
async def dsayi(ctx, member: discord.Member=None):

    member = member or ctx.author

    await ctx.send(
        f"💰 {member.mention} → "
        f"{oyuncu_deger[member.id]}M"
    )

# =========================
# ARA
# =========================

@bot.command()
async def ara(ctx, *, isim):

    res = []

    for m in ctx.guild.members:

        nick = m.nick or m.name

        if isim.lower() in nick.lower():

            res.append(
                f"{m.mention} → {nick}"
            )

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

    await ctx.send(
        f"🏆 Lig: {isim}"
    )

@bot.command()
async def ligtakımekle(ctx):

    roles = ctx.message.role_mentions

    if not roles:
        return await ctx.send("Takım etiketle")

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

    await ctx.send("📅 Fikstür hazır")

@bot.command()
async def hafta(ctx, no: int):

    matches = [x for x in fikstur if x["h"] == no]

    if not matches:
        return await ctx.send("Yok")

    text = ""

    for m in matches:

        text += (
            f"{m['ev'].mention} "
            f"{m['s1']} - {m['s2']} "
            f"{m['dep'].mention}\n"
        )

    await ctx.send(text)

@bot.command()
async def puan(ctx):

    s = sorted(
        puan.items(),
        key=lambda x: x[1]["p"],
        reverse=True
    )

    text = ""

    for i,(id,v) in enumerate(s,1):

        r = ctx.guild.get_role(id)

        text += f"{i}. {r.mention} {v['p']}p\n"

    await ctx.send(text)

# =========================
# HELP
# =========================

@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="⚽ BOT MENÜ",
        description="""
.k @user isim | 1M | ülke | mevki
.dver @user 3
.dsil @user 2
.dsayi @user
.ara isim
.ligekle
.fiksturolustur
        """,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

# =========================
# RUN
# =========================

bot.run(TOKEN)
