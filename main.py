# =========================================================
# NOVA FOOTBALL ROLEPLAY BOT
# Prefix: .
# TOKEN environment variable kullanır
# =========================================================

import os
import random
import difflib
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

# =========================================================
# DATABASE
# =========================================================

warnings = {}

kayit_sayilari = defaultdict(int)

oyuncu_deger = defaultdict(lambda: 1)

antrenman_sayisi = defaultdict(int)

# =========================================================
# LIG DATABASE
# =========================================================

lig_adi = None

lig_takimlari = []

fikstur = []

puan_durumu = defaultdict(
    lambda: {
        "puan": 0,
        "oynanan": 0,
        "galibiyet": 0,
        "beraberlik": 0,
        "maglubiyet": 0,
        "atilan": 0,
        "yenilen": 0
    }
)

# =========================================================
# IDS
# =========================================================

KAYIT_YETKILI = 1503341765178953739

DEGER_YETKILI = 1503341767049740369

ANTRENMAN_KANAL = 1503342068821655653

ROLLER = {

    "Teknik Direktör": 1503341802646802434,
    "Üye": 1503341807310999592,
    "Bayan Üye": 1503341778915299338,
    "Başkan": 1503341801568866315,
    "Futbolcu": 1503341805293277285

}

# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(f"{bot.user} aktif!")

    await bot.change_presence(
        activity=discord.Game(".yardım")
    )

# =========================================================
# ANTRENMAN
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id == ANTRENMAN_KANAL:

        antrenman_sayisi[message.author.id] += 1

        sayi = antrenman_sayisi[message.author.id]

        if sayi < 5:

            embed = discord.Embed(
                title="🏋️ Antrenman Yapıldı",
                description=f"{sayi}/5 tamamlandı.",
                color=discord.Color.orange()
            )

            await message.channel.send(embed=embed)

        else:

            antrenman_sayisi[message.author.id] = 0

            oyuncu_deger[message.author.id] += 3

            member = message.author

            nick = member.nick or member.name

            parts = nick.split("|")

            if len(parts) >= 4:

                isim = parts[0].strip()
                ulke = parts[2].strip()
                mevki = parts[3].strip()

                try:

                    await member.edit(
                        nick=(
                            f"{isim} | "
                            f"{oyuncu_deger[member.id]}M | "
                            f"{ulke} | "
                            f"{mevki}"
                        )
                    )

                except:
                    pass

            embed = discord.Embed(
                title="🔥 Antrenman Tamamlandı",
                description=(
                    f"{member.mention} +3M aldı.\n"
                    f"Yeni değer: "
                    f"{oyuncu_deger[member.id]}M"
                ),
                color=discord.Color.green()
            )

            await message.channel.send(embed=embed)

    await bot.process_commands(message)

# =========================================================
# HELP MENU
# =========================================================

class HelpSelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Moderasyon",
                emoji="🛡️"
            ),

            discord.SelectOption(
                label="Kayıt",
                emoji="📋"
            ),

            discord.SelectOption(
                label="Lig",
                emoji="🏆"
            ),

            discord.SelectOption(
                label="Eğlence",
                emoji="🎮"
            ),

            discord.SelectOption(
                label="Utility",
                emoji="⚙️"
            )

        ]

        super().__init__(
            placeholder="Kategori seç...",
            options=options
        )

    async def callback(self, interaction):

        secim = self.values[0]

        if secim == "Moderasyon":

            text = """
`.ban`
`.kick`
`.mute`
`.unmute`
`.clear`
`.warn`
`.warns`
`.rolver`
`.rolal`
"""

        elif secim == "Kayıt":

            text = """
`.k`
`.kayitsayi`
`.kayittop`
`.dver`
`.dsil`
`.dsayi`
`.dtop`
"""

        elif secim == "Lig":

            text = """
`.ligekle`
`.ligtakımekle`
`.fiksturolustur`
`.hafta`
`.skor`
`.puan`
"""

        elif secim == "Eğlence":

            text = """
`.zar`
`.iq`
`.8ball`
`.slot`
`.ship`
`.öp`
`.tokat`
"""

        else:

            text = """
`.ping`
`.avatar`
`.sunucu`
`.ara`
"""

        embed = discord.Embed(
            title=f"{secim} Komutları",
            description=text,
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed
        )

class HelpView(View):

    def __init__(self):

        super().__init__()

        self.add_item(
            HelpSelect()
        )


@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="🤖 NOVA BOT",
        description=(
            "Kategori seç.\n"
            "Futbol RP evrenine hoş geldin."
        ),
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=HelpView()
    )
@bot.command()
@commands.has_permissions(administrator=True)
async def duyuruyap(ctx, *, mesaj):

    embed = discord.Embed(
        title="ÖNEMLİ",
        description=mesaj,
        color=discord.Color.red()
    )

    

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def dmall(ctx, *, mesaj):

    await ctx.send("📨 DM gönderimi başlatıldı...")

    basarili = 0
    basarisiz = 0

    for member in ctx.guild.members:

        if member.bot:
            continue

        try:
            await member.send(f"📢 Sunucu mesajı:\n\n{mesaj}")
            basarili += 1

        except:
            basarisiz += 1

    await ctx.send(
        f"✅ Gönderildi: {basarili}\n❌ Gönderilemedi: {basarisiz}"
    )
@bot.command()
async def kurallar(ctx):

    embed = discord.Embed(
        title="📜 SUNUCU KURALLARI",
        description=(
            "1️⃣ Saygılı ol. Küfür, hakaret yok. ama ettiğin adam rahatsız olmazsa edebilirsin küfür.\n"
            "2️⃣ Spam ve flood yasak.\n"
            "3️⃣ Reklam yapmak yasak.\n"
            "4️⃣ Yetkililere saygılı davran.\n"
            "5️⃣ Cinsellik ve cinsellikle ilgili içerik paylaşmak yasak.\n"
            "6️⃣ Troll ve rahatsız edici davranış yasak.\n"
            "7️⃣ Discord kurallarına uyulmak zorundadır.\n\n"
            "⚠️ Kurallara uymayanlar cezalandırılır."
        ),
        color=discord.Color.dark_red()
    )

    embed.set_footer(text="Sunucu kurallarını okuyup kabul etmiş sayılırsın.")

    await ctx.send(embed=embed)
# =========================================================
# MODERASYON
# =========================================================

async def can_moderate(ctx, member):

    if member == ctx.author:
        return False

    if member.top_role >= ctx.author.top_role:
        return False

    if member.top_role >= ctx.guild.me.top_role:
        return False

    return True

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):

    if not await can_moderate(ctx, member):
        return await ctx.send("Yetki yetersiz.")

    await member.ban()

    await ctx.send(f"{member} banlandı.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):

    if not await can_moderate(ctx, member):
        return await ctx.send("Yetki yetersiz.")

    await member.kick()

    await ctx.send(f"{member} kicklendi.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):

    await ctx.channel.purge(
        limit=amount + 1
    )

    msg = await ctx.send(
        f"{amount} mesaj silindi."
    )

    await msg.delete(delay=3)

@bot.command()
async def warn(
    ctx,
    member: discord.Member,
    *,
    reason="Sebep yok"
):

    if member.id not in warnings:
        warnings[member.id] = []

    warnings[member.id].append(reason)

    await ctx.send(
        f"{member} warn aldı."
    )

@bot.command()
async def warns(ctx, member: discord.Member):

    w = warnings.get(member.id, [])

    if not w:
        return await ctx.send("Warn yok.")

    await ctx.send("\n".join(w))

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):

    role = discord.utils.get(
        ctx.guild.roles,
        name="Muted"
    )

    if not role:

        role = await ctx.guild.create_role(
            name="Muted"
        )

        for channel in ctx.guild.channels:

            await channel.set_permissions(
                role,
                send_messages=False
            )

    await member.add_roles(role)

    await ctx.send("Susturuldu.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(
        ctx.guild.roles,
        name="Muted"
    )

    await member.remove_roles(role)

    await ctx.send("Susturma kaldırıldı.")

# =========================================================
# SMART ROLVER
# =========================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(
    ctx,
    member_or_role=None,
    *,
    role_name=None
):

    member = None
    query = None

    if ctx.message.reference:

        replied = await ctx.channel.fetch_message(
            ctx.message.reference.message_id
        )

        member = replied.author

        query = member_or_role

    else:

        if not ctx.message.mentions:
            return await ctx.send(
                "Kullanıcı etiketle."
            )

        member = ctx.message.mentions[0]

        query = role_name

    if not query:
        return await ctx.send(
            "Rol belirt."
        )

    role_names = [
        r.name for r in ctx.guild.roles
    ]

    closest = difflib.get_close_matches(
        query,
        role_names,
        n=1,
        cutoff=0.3
    )

    if not closest:
        return await ctx.send(
            "Rol bulunamadı."
        )

    role = discord.utils.get(
        ctx.guild.roles,
        name=closest[0]
    )

    await member.add_roles(role)

    await ctx.send(
        f"{member.mention} → {role.mention}"
    )

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(
    ctx,
    member: discord.Member,
    *,
    role: discord.Role
):

    await member.remove_roles(role)

    await ctx.send("Rol alındı.")

# =========================================================
# KAYIT SISTEMI
# =========================================================

class KayitSelect(discord.ui.Select):

    def __init__(self, uye):

        self.uye = uye

        options = [

            discord.SelectOption(
                label="Teknik Direktör",
                emoji="💼"
            ),

            discord.SelectOption(
                label="Üye",
                emoji="👤"
            ),

            discord.SelectOption(
                label="Bayan Üye",
                emoji="🎀"
            ),

            discord.SelectOption(
                label="Başkan",
                emoji="🤵🏻‍♂️"
            ),

            discord.SelectOption(
                label="Futbolcu",
                emoji="🧩"
            )

        ]

        super().__init__(
            placeholder="Rol seç...",
            options=options
        )

    async def callback(self, interaction):

        role_name = self.values[0]

        role_id = ROLLER[role_name]

        role = interaction.guild.get_role(
            role_id
        )

        await self.uye.add_roles(role)

        kayit_sayilari[
            interaction.user.id
        ] += 1

        embed = discord.Embed(
            title="✅ Kayıt Yapıldı",
            description=(
                f"{self.uye.mention} → "
                f"{role.mention}"
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

class KayitView(View):

    def __init__(self, uye):

        super().__init__(timeout=60)

        self.add_item(
            KayitSelect(uye)
        )

@bot.command()
@commands.has_role(KAYIT_YETKILI)
async def k(ctx, member: discord.Member, *, isim):

    await member.edit(nick=isim)

    embed = discord.Embed(
        title="📋 Kayıt Paneli",
        description=(
            f"👤 {member.mention}\n"
            f"🧩 {isim}"
        ),
        color=discord.Color.blurple()
    )

    await ctx.send(
        embed=embed,
        view=KayitView(member)
    )

@bot.command()
async def kayitsayi(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    await ctx.send(
        f"Kayıt sayısı: "
        f"{kayit_sayilari[member.id]}"
    )

@bot.command()
async def kayittop(ctx):

    sorted_users = sorted(
        kayit_sayilari.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = ""

    for i, (uid, amount) in enumerate(
        sorted_users[:10],
        start=1
    ):

        user = bot.get_user(uid)

        text += (
            f"{i}. {user} → "
            f"{amount}\n"
        )

    embed = discord.Embed(
        title="🏆 Kayıt Top",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# =========================================================
# DEGER SISTEMI
# =========================================================

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dver(
    ctx,
    member: discord.Member,
    amount: int
):

    oyuncu_deger[member.id] += amount

    nick = member.nick

    if nick and "|" in nick:

        parts = nick.split("|")

        if len(parts) >= 4:

            isim = parts[0].strip()
            ulke = parts[2].strip()
            mevki = parts[3].strip()

            await member.edit(
                nick=(
                    f"{isim} | "
                    f"{oyuncu_deger[member.id]}M | "
                    f"{ulke} | "
                    f"{mevki}"
                )
            )

    await ctx.send(
        f"Yeni değer: "
        f"{oyuncu_deger[member.id]}M"
    )

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dsil(
    ctx,
    member: discord.Member,
    amount: int
):

    if oyuncu_deger[member.id] <= 1:
        return await ctx.send(
            "1M altına düşemez."
        )

    oyuncu_deger[member.id] -= amount

    if oyuncu_deger[member.id] < 1:
        oyuncu_deger[member.id] = 1

    await ctx.send(
        f"Yeni değer: "
        f"{oyuncu_deger[member.id]}M"
    )

@bot.command()
async def dsayi(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    await ctx.send(
        f"{oyuncu_deger[member.id]}M"
    )

@bot.command()
async def dtop(ctx):

    sorted_users = sorted(
        oyuncu_deger.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = ""

    for i, (uid, amount) in enumerate(
        sorted_users[:10],
        start=1
    ):

        user = bot.get_user(uid)

        text += (
            f"{i}. {user} → "
            f"{amount}M\n"
        )

    embed = discord.Embed(
        title="💰 Değer Top",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# =========================================================
# LIG SISTEMI
# =========================================================

@bot.command()
async def ligekle(ctx, *, isim):

    global lig_adi

    lig_adi = isim

    await ctx.send(
        f"Lig oluşturuldu: {isim}"
    )

@bot.command(name="ligtakımekle")
async def ligtakimekle(ctx):

    global lig_takimlari

    mentions = ctx.message.role_mentions

    if not mentions:
        return await ctx.send(
            "Takım etiketle."
        )

    for role in mentions:

        if role not in lig_takimlari:
            lig_takimlari.append(role)

    await ctx.send(
        f"{len(mentions)} takım eklendi."
    )

@bot.command()
async def fiksturolustur(ctx):

    global fikstur
    fikstur.clear()

    takimlar = lig_takimlari.copy()

    # Tek sayıda takım varsa bye ekle
    if len(takimlar) % 2 == 1:
        takimlar.append(None)

    n = len(takimlar)
    rounds = n - 1
    half = n // 2

    for hafta in range(rounds):

        for i in range(half):

            ev = takimlar[i]
            dep = takimlar[n - 1 - i]

            if ev is None or dep is None:
                continue

            fikstur.append({
                "hafta": hafta + 1,
                "ev": ev,
                "dep": dep,
                "s1": None,
                "s2": None
            })

        # Döndür (round-robin sistemi)
        takimlar = (
            [takimlar[0]] +
            [takimlar[-1]] +
            takimlar[1:-1]
        )

    await ctx.send("Fikstür düzgün şekilde oluşturuldu. Artık hafta 1 yalnız hissetmeyecek.")

@bot.command()
async def hafta(ctx, number: int):

    matches = [
        x for x in fikstur
        if x["hafta"] == number
    ]

    if not matches:
        return await ctx.send(
            "Hafta bulunamadı."
        )

    text = ""

    for m in matches:

        ev = m["ev"]
        dep = m["dep"]

        if m["s1"] is None:
            text += (
                f"{ev.mention} vs "
                f"{dep.mention} — Oynanmadı\n"
            )
        else:
            text += (
                f"{ev.mention} "
                f"{m['s1']}-{m['s2']} "
                f"{dep.mention}\n"
            )

    embed = discord.Embed(
        title=f"📅 Hafta {number}",
        description=text,
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

@bot.command()
async def skor(
    ctx,
    rol1: discord.Role,
    rol2: discord.Role,
    *,
    sonuc: str
):

    if sonuc.lower() == "rastgele":
        s1 = random.randint(0, 5)
        s2 = random.randint(0, 5)
    else:
        try:
            parcalar = sonuc.strip().split("-")
            s1 = int(parcalar[0])
            s2 = int(parcalar[1])
        except:
            return await ctx.send(
                "Geçersiz format. Örnek: `3-2` ya da `rastgele`"
            )

    # Puan güncelle
    puan_durumu[rol1.id]["oynanan"] += 1
    puan_durumu[rol2.id]["oynanan"] += 1
    puan_durumu[rol1.id]["atilan"] += s1
    puan_durumu[rol1.id]["yenilen"] += s2
    puan_durumu[rol2.id]["atilan"] += s2
    puan_durumu[rol2.id]["yenilen"] += s1

    if s1 > s2:
        puan_durumu[rol1.id]["puan"] += 3
        puan_durumu[rol1.id]["galibiyet"] += 1
        puan_durumu[rol2.id]["maglubiyet"] += 1
    elif s2 > s1:
        puan_durumu[rol2.id]["puan"] += 3
        puan_durumu[rol2.id]["galibiyet"] += 1
        puan_durumu[rol1.id]["maglubiyet"] += 1
    else:
        puan_durumu[rol1.id]["puan"] += 1
        puan_durumu[rol2.id]["puan"] += 1
        puan_durumu[rol1.id]["beraberlik"] += 1
        puan_durumu[rol2.id]["beraberlik"] += 1

    embed = discord.Embed(
        title="⚽ Maç Sonucu",
        description=(
            f"{rol1.mention} "
            f"**{s1} - {s2}** "
            f"{rol2.mention}"
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.command()
async def puan(ctx):

    if len(lig_takimlari) == 0:
        return await ctx.send("Lig yok.")

    # Her takımı garanti listeye sok
    for role in lig_takimlari:

        if role.id not in puan_durumu:
            puan_durumu[role.id]  # otomatik 0 başlatır

    siralama = sorted(
        lig_takimlari,
        key=lambda r: puan_durumu[r.id]["puan"],
        reverse=True
    )

    text = ""

    for i, role in enumerate(siralama, start=1):

        stats = puan_durumu[role.id]

        text += (
            f"{i}. {role.mention}\n"
            f"🏆 Puan: {stats['puan']}\n"
            f"⚽ O: {stats['oynanan']} G:{stats['galibiyet']} B:{stats['beraberlik']} M:{stats['maglubiyet']}\n\n"
        )

    embed = discord.Embed(
        title=f"🏆 {lig_adi or 'Lig'} Puan Tablosu",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)
@bot.command()
async def macsonuclari(ctx):

    if len(fikstur) == 0:
        return await ctx.send("Fikstür yok.")

    text = ""

    for m in fikstur:

        ev = m["ev"]
        dep = m["dep"]

        if m["s1"] is None:

            text += f"⏳ {ev.mention} vs {dep.mention} (Oynanmadı)\n"

        else:

            text += f"✅ {ev.mention} {m['s1']} - {m['s2']} {dep.mention}\n"

    embed = discord.Embed(
        title="📊 Tüm Maçlar",
        description=text,
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed)

# =========================================================
# ARA
# =========================================================

@bot.command()
async def ara(ctx, *, isim):

    bulunanlar = []

    for member in ctx.guild.members:

        nick = member.nick or member.name

        if isim.lower() in nick.lower():

            bulunanlar.append(
                f"{member.mention} → `{nick}`"
            )

    if not bulunanlar:
        return await ctx.send(
            "Bulunamadı."
        )

    embed = discord.Embed(
        title=f"🔎 {isim}",
        description="\n".join(
            bulunanlar[:20]
        ),
        color=discord.Color.blurple()
    )

    await ctx.send(embed=embed)

# =========================================================
# EGLENCE
# =========================================================

@bot.command()
async def zar(ctx):

    await ctx.send(
        f"🎲 {random.randint(1,6)}"
    )

@bot.command()
async def iq(ctx):

    await ctx.send(
        f"🧠 IQ: "
        f"{random.randint(1,300)}"
    )

@bot.command(name="8ball")
async def eightball(ctx, *, question):

    answers = [
        "Evet",
        "Hayır",
        "Belki",
        "Kesinlikle"
    ]

    await ctx.send(
        random.choice(answers)
    )

@bot.command()
async def slot(ctx):

    emojis = [
        "🍎",
        "🍇",
        "🍒"
    ]

    sonuc = [
        random.choice(emojis)
        for _ in range(3)
    ]

    await ctx.send(
        " | ".join(sonuc)
    )

@bot.command()
async def ship(
    ctx,
    m1: discord.Member,
    m2: discord.Member
):

    await ctx.send(
        f"❤️ %{random.randint(1,100)}"
    )

@bot.command()
async def öp(
    ctx,
    member: discord.Member
):

    await ctx.send(
        f"😘 {member.mention}"
    )

@bot.command()
async def tokat(
    ctx,
    member: discord.Member
):

    await ctx.send(
        f"👋 {member.mention}"
    )

# =========================================================
# UTILITY
# =========================================================

@bot.command()
async def ping(ctx):

    await ctx.send(
        f"🏓 "
        f"{round(bot.latency*1000)}ms"
    )

@bot.command()
async def avatar(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    embed = discord.Embed()

    embed.set_image(
        url=member.display_avatar.url
    )

    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):

    guild = ctx.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.green()
    )

    embed.add_field(
        name="Üye",
        value=guild.member_count
    )

    await ctx.send(embed=embed)

# =========================================================
# RUN
# =========================================================

bot.run(TOKEN)
