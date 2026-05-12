# =========================================================
# NOVA FOOTBALL ROLEPLAY BOT
# Prefix: .
# TOKEN environment variable kullanır
# =========================================================

import os
import random
import difflib
import discord
import time

from collections import defaultdict
from discord.ext import commands
from discord.ui import View, Select

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

afk_users = {}

from discord.ext import commands

def has_deger_yetki(ctx):
    return DEGER_YETKILI in [r.id for r in ctx.author.roles]

def parse_deger(metin):
    metin = metin.upper().replace(",", "").replace(" ", "")
    multi = 1
    if metin.endswith("B"):
        multi = 1_000_000_000
        metin = metin[:-1]
    elif metin.endswith("M"):
        multi = 1_000_000
        metin = metin[:-1]
    elif metin.endswith("K"):
        multi = 1_000
        metin = metin[:-1]
    try:
        return float(metin) * multi
    except ValueError:
        return None

def format_deger(sayi):
    if sayi >= 1_000_000_000:
        val = sayi / 1_000_000_000
        return f"{int(val)}B" if val.is_integer() else f"{val:.1f}B"
    elif sayi >= 1_000_000:
        val = sayi / 1_000_000
        return f"{int(val)}M" if val.is_integer() else f"{val:.1f}M"
    elif sayi >= 1_000:
        val = sayi / 1_000
        return f"{int(val)}K" if val.is_integer() else f"{val:.1f}K"
    return str(int(sayi))

def deger_isle(isim, miktar_str, islem):
    parcalar = [p.strip() for p in isim.split("|")]
    if len(parcalar) < 2:
        return None, "İsim formatı hatalı! Format: Ad | 1M | ..."
    mevcut = parse_deger(parcalar[1])
    if mevcut is None:
        return None, "Mevcut değer okunamadı!"
    eklenecek = parse_deger(miktar_str)
    if eklenecek is None:
        return None, f"{miktar_str} geçersiz bir değer!"
    yeni = mevcut + eklenecek if islem == "ekle" else mevcut - eklenecek
    if yeni < 0:
        yeni = 0
    parcalar[1] = format_deger(yeni)
    islem_str = f"+{miktar_str}" if islem == "ekle" else f"-{miktar_str}"
    return " | ".join(parcalar), islem_str

# =========================================================
# DATABASE
# =========================================================

warnings = {}

kayit_sayilari = defaultdict(int)

oyuncu_deger = defaultdict(lambda: 1)

antrenman_sayisi = defaultdict(int)
gol = defaultdict(int)

asist = defaultdict(int)

golyemeyen = defaultdict(int)

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
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # AFK'dan çıkış
    if message.author.id in afk_users:

        data = afk_users.pop(message.author.id)

        embed = discord.Embed(
            title="👋 AFK BİTTİ",
            description=(
                f"{message.author.mention} geri döndü\n"
                f"AFK Sebebi: {data['reason']}"
            ),
            color=discord.Color.green()
        )

        await message.channel.send(embed=embed)

    # AFK mention kontrol
    for user in message.mentions:

        if user.id in afk_users:

            data = afk_users[user.id]

            embed = discord.Embed(
                title="😴 AFK KULLANICI",
                description=(
                    f"{user.name} şu anda AFK\n"
                    f"Sebep: {data['reason']}"
                ),
                color=discord.Color.orange()
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

@bot.command()
async def afk(ctx, *, reason="AFK"):

    afk_users[ctx.author.id] = {
        "reason": reason,
        "time": time.time()
    }

    embed = discord.Embed(
        title="😴 AFK MODU AKTİF",
        description=f"{ctx.author.mention} artık AFK\nSebep: {reason}",
        color=discord.Color.dark_gray()
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
async def şart(ctx):

    if ctx.channel.id != 1503342028170199100:
        return await ctx.send("Bu komut burada kullanılamaz.")

    embed = discord.Embed(
        title="📜 SUNUCU KAYIT ŞARTLARI",
        description=(
            "Sunucuya tam erişim için aşağıdaki adımları tamamla:\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🏷️ <#1503342044834168914> kanalından 2 rol al\n\n"
            "🗳️ <#1503342033526456431> kanalında oy ver\n\n"
            "✔️ <#1503342039889088622> kanalında tik butonuna bas\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ Bu işlemler tamamlanmadan kayıt olunmaz."
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

    
@bot.command()
@commands.has_permissions(administrator=True)
async def title(ctx, title, *, mesaj):

    embed = discord.Embed(
        title=title,
        description=mesaj,
        color=discord.Color.blue()
    )

    

    await ctx.send(embed=embed)
@bot.command()
async def takimlar(ctx):

    await ctx.guild.chunk()

    embed = discord.Embed(
        title="⚽ TAKIM DURUMU",
        color=discord.Color.gold()
    )

    bos_mu = True

    for isim, role_id in TAKIMLAR.items():

        role = ctx.guild.get_role(role_id)

        if role is None:
            embed.add_field(
                name=isim,
                value="❌ ROLE BULUNAMADI (ID HATALI)",
                inline=False
            )
            bos_mu = False
            continue

        bos_mu = False

        baskan_var = False
        td_var = False

        for u in role.members:

            if any(r.id == BASKAN_ROL_ID for r in u.roles):
                baskan_var = True

            if any(r.id == TD_ROL_ID for r in u.roles):
                td_var = True

        if baskan_var and td_var:
            durum = "🟢 DOLU"
        elif td_var:
            durum = "🟡 TD VAR"
        elif baskan_var:
            durum = "🟠 BAŞKAN VAR"
        else:
            durum = "🔴 BOŞ"

        embed.add_field(
            name=isim,
            value=durum,
            inline=False
        )

    if bos_mu:
        embed.description = "Hiç takım bulunamadı. (Role ID'ler yanlış olabilir)"

    await ctx.send(embed=embed)
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
# LIG SISTEMI
# =========================================================

@bot.command()

async def ligekle(ctx, *, isim):

    global lig_adi

    lig_adi = isim

    await ctx.send(f"🏆 Lig: {isim}")

@bot.command()

async def ligtakımekle(ctx):

    global lig_takimlari

    for r in ctx.message.role_mentions:

        if r not in lig_takimlari:

            lig_takimlari.append(r)

    await ctx.send("Takımlar eklendi")

@bot.command()

async def fiksturolustur(ctx):

    global fikstur

    fikstur.clear()

    teams = lig_takimlari.copy()

    if len(teams) % 2 == 1:

        teams.append(None)

    n = len(teams)

    half = n // 2

    for hafta in range(n - 1):

        for i in range(half):

            ev = teams[i]

            dep = teams[n - 1 - i]

            if ev and dep:

                fikstur.append({

                    "hafta": hafta + 1,

                    "ev": ev,

                    "dep": dep,

                    "s1": None,

                    "s2": None,

                    "played": False

                })

        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    await ctx.send("Fikstür hazır")
    
@bot.command()

async def hafta(ctx, number: int):

    matches = [m for m in fikstur if m["hafta"] == number]

    if not matches:

        return await ctx.send("Hafta yok")

    text = ""

    for m in matches:

        ev = m["ev"].name

        dep = m["dep"].name

        if not m["played"]:

            text += f"⏳ {ev} vs {dep}\n"

        else:

            text += f"✅ {ev} {m['s1']}-{m['s2']} {dep}\n"

    await ctx.send(text)

# =========================================================

# SKOR (TEK GİRİŞ + DUPLICATE ENGEL)

# =========================================================

@bot.command()

async def skor(ctx, hafta_no: int, ev: discord.Role, dep: discord.Role, sonuc: str):

    for m in fikstur:

        if m["hafta"] == hafta_no and m["ev"] == ev and m["dep"] == dep:

            if m["played"]:

                return await ctx.send("⚠ Bu maç zaten girilmiş")

            s1, s2 = map(int, sonuc.split("-"))
            # Clean sheet (gol yememe)
if s2 == 0:
    clean_sheet[ev.id] += 1

if s1 == 0:
    clean_sheet[dep.id] += 1

            m["s1"] = s1

            m["s2"] = s2

            m["played"] = True

            puan_durumu[ev.id]["oynanan"] += 1

            puan_durumu[dep.id]["oynanan"] += 1

            if s1 > s2:

                puan_durumu[ev.id]["puan"] += 3

                puan_durumu[ev.id]["galibiyet"] += 1

                puan_durumu[dep.id]["maglubiyet"] += 1

            elif s2 > s1:

                puan_durumu[dep.id]["puan"] += 3

                puan_durumu[dep.id]["galibiyet"] += 1

                puan_durumu[ev.id]["maglubiyet"] += 1

            else:

                puan_durumu[ev.id]["puan"] += 1

                puan_durumu[dep.id]["puan"] += 1

            return await ctx.send("Skor girildi")

    await ctx.send("Maç bulunamadı")

# =========================================================

# SKOR DÜZENLE

# =========================================================

@bot.command()

async def skordüzenle(ctx, hafta_no: int, ev: discord.Role, dep: discord.Role, sonuc: str):

    for m in fikstur:

        if m["hafta"] == hafta_no and m["ev"] == ev and m["dep"] == dep:

            old1, old2 = m["s1"], m["s2"]

            if not m["played"]:

                return await ctx.send("Önce skor girilmeli")

            new1, new2 = map(int, sonuc.split("-"))

            m["s1"], m["s2"] = new1, new2

            return await ctx.send("Düzenlendi")

    await ctx.send("Bulunamadı")

# =========================================================

# STAT KOMUTLARI

# =========================================================

@bot.command()

async def golekle(ctx, member: discord.Member, amount: int):

    gol[member.id] += amount

    await ctx.send("Gol eklendi")

@bot.command()

async def asistekle(ctx, member: discord.Member, amount: int):

    asist[member.id] += amount

    await ctx.send("Asist eklendi")

@bot.command()

async def golyenmeyenmaç(ctx, member: discord.Member, amount: int):

    golyemeyen[member.id] += amount

    await ctx.send("Eklendi")

@bot.command()

async def golsayı(ctx, member: discord.Member):

    await ctx.send(f"⚽ {gol[member.id]}")

@bot.command()

async def asistsayı(ctx, member: discord.Member):

    await ctx.send(f"🎯 {asist[member.id]}")
@bot.command()
async def golyenmeyenmac(ctx, member: discord.Member):

    await ctx.send(
        f"🧤 Gol yemediği maç: {clean_sheet[member.id]}"
    )
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
