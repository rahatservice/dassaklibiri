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

# ==================================================
# DATABASE
# ==================================================

warnings = {}

kayit_sayilari = defaultdict(int)
deger_sayilari = defaultdict(int)

oyuncu_deger = defaultdict(lambda: 1)

antrenman_sayisi = defaultdict(int)

# ==================================================
# IDS
# ==================================================

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

# ==================================================
# READY
# ==================================================

@bot.event
async def on_ready():

    print(f"{bot.user} aktif!")

    await bot.change_presence(
        activity=discord.Game(".yardım")
    )

# ==================================================
# ANTRENMAN SISTEMI
# ==================================================

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
                description=f"`{sayi}/5` tamamlandı.",
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

                yeni_deger = (
                    f"{oyuncu_deger[member.id]}M"
                )

                yeni_nick = (
                    f"{isim} | "
                    f"{yeni_deger} | "
                    f"{ulke} | "
                    f"{mevki}"
                )

                try:

                    await member.edit(
                        nick=yeni_nick
                    )

                except:
                    pass

            embed = discord.Embed(
                title="🔥 Antrenman Tamamlandı",
                description=(
                    f"{member.mention} oyuncusuna "
                    f"`+3M` eklendi.\n\n"
                    f"Yeni değer: "
                    f"`{oyuncu_deger[member.id]}M`"
                ),
                color=discord.Color.green()
            )

            await message.channel.send(
                embed=embed
            )

    await bot.process_commands(message)

# ==================================================
# ERROR
# ==================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌ Yetkin yok.")

    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("❌ Kullanıcı bulunamadı.")

    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("❌ Eksik argüman.")

# ==================================================
# YETKI CHECK
# ==================================================

async def can_moderate(ctx, member):

    if member == ctx.author:
        return False

    if member.top_role >= ctx.author.top_role:
        return False

    if member.top_role >= ctx.guild.me.top_role:
        return False

    return True

# ==================================================
# HELP MENU
# ==================================================

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
                label="Değer",
                emoji="💰"
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

        c = self.values[0]

        if c == "Moderasyon":

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
`.nuke`
"""

            color = discord.Color.red()

        elif c == "Kayıt":

            text = """
`.k`
`.kayitsayi`
`.kayittop`
"""

            color = discord.Color.blurple()

        elif c == "Değer":

            text = """
`.dver`
`.dsil`
`.dsayi`
`.dtop`
"""

            color = discord.Color.gold()

        elif c == "Eğlence":

            text = """
`.zar`
`.iq`
`.8ball`
`.slot`
`.ship`
`.öp`
`.tokat`
`.hackle`
"""

            color = discord.Color.purple()

        else:

            text = """
`.ping`
`.avatar`
`.sunucu`
`.kullanıcı`
`.botbilgi`
"""

            color = discord.Color.green()

        embed = discord.Embed(
            title=f"{c} Komutları",
            description=text,
            color=color
        )

        embed.set_footer(
            text="Prefix: ."
        )

        await interaction.response.edit_message(
            embed=embed
        )

class HelpView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(HelpSelect())

@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="🤖 Yardım Menüsü",
        description=(
            "Kategori seç.\n\n"
            "🛡️ Moderasyon\n"
            "📋 Kayıt\n"
            "💰 Değer\n"
            "🎮 Eğlence\n"
            "⚙️ Utility"
        ),
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=bot.user.display_avatar.url
    )

    await ctx.send(
        embed=embed,
        view=HelpView()
    )

# ==================================================
# MODERASYON
# ==================================================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("❌ Yapamazsın.")

    await member.ban(reason=reason)

    await ctx.send(
        f"🔨 {member} banlandı."
    )

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sebep yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("❌ Yapamazsın.")

    await member.kick(reason=reason)

    await ctx.send(
        f"👢 {member} kicklendi."
    )

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):

    await ctx.channel.purge(
        limit=amount + 1
    )

    await ctx.send(
        f"🧹 {amount} mesaj silindi.",
        delete_after=3
    )

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

    await ctx.send(
        f"🔇 {member} susturuldu."
    )

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(
        ctx.guild.roles,
        name="Muted"
    )

    if role in member.roles:

        await member.remove_roles(role)

    await ctx.send(
        f"🔊 {member} susturması kaldırıldı."
    )

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Sebep yok"):

    if member.id not in warnings:
        warnings[member.id] = []

    warnings[member.id].append(reason)

    await ctx.send(
        f"⚠️ {member} warn aldı."
    )

@bot.command()
async def warns(ctx, member: discord.Member):

    w = warnings.get(member.id, [])

    if not w:
        return await ctx.send("Warn yok.")

    await ctx.send("\n".join(w))

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):

    channel = ctx.channel

    new = await channel.clone()

    await channel.delete()

    await new.send(
        "💥 Kanal resetlendi."
    )

# ==================================================
# SMART ROLVER
# ==================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member_or_role=None, *, role_name=None):

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
                "❌ Kullanıcı etiketle."
            )

        member = ctx.message.mentions[0]

        query = role_name

    if not query:
        return await ctx.send(
            "❌ Rol belirt."
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
            "❌ Rol bulunamadı."
        )

    role = discord.utils.get(
        ctx.guild.roles,
        name=closest[0]
    )

    if role >= ctx.author.top_role:
        return await ctx.send(
            "❌ Yetki yok."
        )

    await member.add_roles(role)

    await ctx.send(
        f"✅ {member.mention} → {role.mention}"
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

    await ctx.send(
        f"❌ {role.name} alındı."
    )

# ==================================================
# KAYIT SISTEMI
# ==================================================

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
                f"{self.uye.mention} kişisine "
                f"{role.mention} verildi."
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

class KayitView(discord.ui.View):

    def __init__(self, uye):

        super().__init__(timeout=60)

        self.add_item(KayitSelect(uye))

@bot.command()
@commands.has_role(KAYIT_YETKILI)
async def k(
    ctx,
    member: discord.Member,
    isim,
    deger,
    ulke,
    mevki
):

    oyuncu_deger[member.id] = int(
        deger.replace("M", "")
    )

    await member.edit(
        nick=f"{isim} | {deger} | {ulke} | {mevki}"
    )

    embed = discord.Embed(
        title="📋 Kayıt Paneli",
        description=(
            f"Kullanıcı: {member.mention}\n"
            f"İsim: {isim}\n"
            f"Değer: {deger}\n"
            f"Ülke: {ulke}\n"
            f"Mevki: {mevki}"
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

    sayi = kayit_sayilari[member.id]

    await ctx.send(
        f"📋 {member.mention} kayıt sayısı: `{sayi}`"
    )

@bot.command()
async def kayittop(ctx):

    if not kayit_sayilari:
        return await ctx.send("Veri yok.")

    sorted_users = sorted(
        kayit_sayilari.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = ""

    for i, (user_id, amount) in enumerate(
        sorted_users[:10],
        start=1
    ):

        user = bot.get_user(user_id)

        text += (
            f"{i}. {user} → `{amount}` kayıt\n"
        )

    embed = discord.Embed(
        title="🏆 Kayıt Top",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# ==================================================
# DEGER SISTEMI
# ==================================================

@bot.command()
@commands.has_role(DEGER_YETKILI)
async def dver(
    ctx,
    member: discord.Member,
    amount: int
):

    oyuncu_deger[member.id] += amount

    deger_sayilari[
        ctx.author.id
    ] += amount

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
        f"💰 Yeni değer: "
        f"`{oyuncu_deger[member.id]}M`"
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
        f"📉 Yeni değer: "
        f"`{oyuncu_deger[member.id]}M`"
    )

@bot.command()
async def dsayi(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    await ctx.send(
        f"💰 Değer: "
        f"`{oyuncu_deger[member.id]}M`"
    )

@bot.command()
async def dtop(ctx):

    sorted_users = sorted(
        oyuncu_deger.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = ""

    for i, (user_id, amount) in enumerate(
        sorted_users[:10],
        start=1
    ):

        user = bot.get_user(user_id)

        text += (
            f"{i}. {user} → `{amount}M`\n"
        )

    embed = discord.Embed(
        title="💎 Değer Top",
        description=text,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# ==================================================
# EGLENCE
# ==================================================

@bot.command()
async def zar(ctx):

    await ctx.send(
        f"🎲 {random.randint(1,6)}"
    )

@bot.command()
async def iq(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    await ctx.send(
        f"🧠 IQ: {random.randint(1,300)}"
    )

@bot.command(name="8ball")
async def eightball(ctx, *, question):

    answers = [
        "Evet",
        "Hayır",
        "Belki",
        "Kesinlikle",
        "İmkansız"
    ]

    await ctx.send(
        f"🎱 {random.choice(answers)}"
    )

@bot.command()
async def slot(ctx):

    emojis = [
        "🍎",
        "🍌",
        "🍇"
    ]

    result = [
        random.choice(emojis)
        for _ in range(3)
    ]

    await ctx.send(
        " | ".join(result)
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

@bot.command()
async def hackle(
    ctx,
    member: discord.Member
):

    stages = [

        "IP bulunuyor...",
        "Token çekiliyor...",
        "Hackleniyor..."
    ]

    msg = await ctx.send("Başladı")

    for s in stages:

        await msg.edit(content=s)

    await msg.edit(
        content=f"{member} hacklendi 💀"
    )

# ==================================================
# UTILITY
# ==================================================

@bot.command()
async def ping(ctx):

    await ctx.send(
        f"🏓 {round(bot.latency*1000)}ms"
    )

@bot.command()
async def avatar(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    embed = discord.Embed(
        title=str(member)
    )

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

@bot.command()
async def kullanıcı(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    embed = discord.Embed(
        title=str(member)
    )

    embed.add_field(
        name="ID",
        value=member.id
    )

    await ctx.send(embed=embed)

@bot.command()
async def botbilgi(ctx):

    await ctx.send(
        f"🤖 Sunucu sayısı: "
        f"`{len(bot.guilds)}`"
    )

# ==================================================
# BOT RUN
# ==================================================

bot.run(TOKEN)
