import os
import random
import difflib
import discord
from discord.ext import commands
from discord.ui import View, Select
from datetime import timedelta

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

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
# ERROR SYSTEM
# ==================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("Bunun için yetkin yok.")

    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("Üye bulunamadı.")

    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("Eksik argüman girdin.")

    raise error

# ==================================================
# YETKI KONTROL
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
# YARDIM MENUSU
# ==================================================

class HelpSelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Moderasyon",
                emoji="🛡️"
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

    async def callback(self, interaction: discord.Interaction):

        value = self.values[0]

        if value == "Moderasyon":

            desc = """
`.ban`
`.kick`
`.timeout`
`.untimeout`
`.sil`
`.kilit`
`.aç`
`.slowmode`
`.rolver`
`.rolal`
"""

        elif value == "Eğlence":

            desc = """
`.zar`
`.yazitura`
`.iq`
`.8ball`
`.slot`
`.ship`
`.öp`
`.tokat`
`.hackle`
"""

        else:

            desc = """
`.ping`
`.avatar`
`.sunucu`
`.kullanıcı`
`.botbilgi`
"""

        embed = discord.Embed(
            title=f"{value} Komutları",
            description=desc,
            color=discord.Color.blurple()
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
        title="📚 Yardım Menüsü",
        description="Aşağıdan kategori seç.",
        color=discord.Color.green()
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
async def ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):

    if not await can_moderate(ctx, member):
        return await ctx.send(
            "Bu kişiyi banlayamazsın."
        )

    await member.ban(reason=reason)

    embed = discord.Embed(
        title="🔨 Banlandı",
        description=f"{member.mention} banlandı.\nSebep: {reason}",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):

    if not await can_moderate(ctx, member):
        return await ctx.send(
            "Bu kişiyi kickleyemezsin."
        )

    await member.kick(reason=reason)

    embed = discord.Embed(
        title="👢 Kicklendi",
        description=f"{member.mention} kicklendi.\nSebep: {reason}",
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(
    ctx,
    member: discord.Member,
    dakika: int,
    *,
    reason="Sebep belirtilmedi"
):

    if not await can_moderate(ctx, member):
        return await ctx.send(
            "Bu kişiye timeout atamazsın."
        )

    duration = timedelta(minutes=dakika)

    await member.timeout(
        duration,
        reason=reason
    )

    embed = discord.Embed(
        title="⏳ Timeout",
        description=(
            f"{member.mention} "
            f"{dakika} dakika susturuldu."
        ),
        color=discord.Color.yellow()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):

    await member.timeout(None)

    await ctx.send(
        f"{member.mention} timeout kaldırıldı."
    )

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, amount: int):

    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(
        f"{amount} mesaj silindi."
    )

    await msg.delete(delay=3)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def kilit(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )

    await ctx.send("🔒 Kanal kilitlendi.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def aç(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )

    await ctx.send("🔓 Kanal açıldı.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):

    await ctx.channel.edit(
        slowmode_delay=seconds
    )

    await ctx.send(
        f"Slowmode {seconds} saniye oldu."
    )

# ==================================================
# GELISMIS ROLVER
# ==================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member_or_role=None, *, role_name=None):

    member = None
    role_query = None

    # =========================
    # YANIT SISTEMI
    # =========================

    if ctx.message.reference:

        replied_message = await ctx.channel.fetch_message(
            ctx.message.reference.message_id
        )

        member = replied_message.author

        role_query = member_or_role

    else:

        if not ctx.message.mentions:
            return await ctx.send(
                "Bir kullanıcı etiketlemelisin "
                "veya mesaja yanıt vermelisin."
            )

        member = ctx.message.mentions[0]

        role_query = role_name

    if not role_query:
        return await ctx.send(
            "Rol belirtmelisin."
        )

    # =========================
    # EN YAKIN ROL BULMA
    # =========================

    role_names = [r.name for r in ctx.guild.roles]

    closest = difflib.get_close_matches(
        role_query,
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

    # =========================
    # YETKI KONTROL
    # =========================

    if role >= ctx.author.top_role:
        return await ctx.send(
            "Bu rolü veremezsin."
        )

    if role >= ctx.guild.me.top_role:
        return await ctx.send(
            "Bu rol benim rolümden yüksek."
        )

    # =========================
    # ROL VER
    # =========================

    await member.add_roles(role)

    embed = discord.Embed(
        title="✅ Rol Verildi",
        description=(
            f"{member.mention} kişisine "
            f"`{role.name}` rolü verildi."
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

# ==================================================
# ROL AL
# ==================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, *, role: discord.Role):

    if role >= ctx.author.top_role:
        return await ctx.send(
            "Bu rolü alamazsın."
        )

    await member.remove_roles(role)

    await ctx.send(
        f"{member.mention} kişisinden "
        f"{role.name} alındı."
    )

# ==================================================
# EGLENCE
# ==================================================

@bot.command()
async def zar(ctx):

    await ctx.send(
        f"🎲 Zar sonucu: "
        f"{random.randint(1,6)}"
    )

@bot.command()
async def yazitura(ctx):

    await ctx.send(
        random.choice([
            "Yazı",
            "Tura"
        ])
    )

@bot.command()
async def iq(ctx, member: discord.Member=None):

    member = member or ctx.author

    iq = random.randint(1,300)

    await ctx.send(
        f"{member.mention} IQ seviyesi: `{iq}`"
    )

@bot.command(name="8ball")
async def eightball(ctx, *, question):

    answers = [
        "Evet",
        "Hayır",
        "Belki",
        "Kesinlikle",
        "İmkansız",
        "Büyük ihtimalle"
    ]

    await ctx.send(
        random.choice(answers)
    )

@bot.command()
async def slot(ctx):

    emojis = [
        "🍎",
        "🍌",
        "🍇",
        "💎"
    ]

    result = [
        random.choice(emojis),
        random.choice(emojis),
        random.choice(emojis)
    ]

    text = " | ".join(result)

    if len(set(result)) == 1:

        await ctx.send(
            f"{text}\nKazandın!"
        )

    else:

        await ctx.send(
            f"{text}\nKaybettin!"
        )

@bot.command()
async def ship(
    ctx,
    member1: discord.Member,
    member2: discord.Member
):

    percent = random.randint(1,100)

    await ctx.send(
        f"❤️ {member1.name} + "
        f"{member2.name} = %{percent}"
    )

@bot.command()
async def öp(ctx, member: discord.Member):

    await ctx.send(
        f"😘 {ctx.author.mention} "
        f"{member.mention} kişisini öptü."
    )

@bot.command()
async def tokat(ctx, member: discord.Member):

    await ctx.send(
        f"👋 {ctx.author.mention} "
        f"{member.mention} kişisine tokat attı."
    )

@bot.command()
async def hackle(ctx, member: discord.Member):

    stages = [
        "IP bulunuyor...",
        "Discord tokeni çekiliyor...",
        "Minecraft hesabı ele geçiriliyor...",
        "Annesinin kızlık soyadı bulunuyor..."
    ]

    msg = await ctx.send(
        "Hack işlemi başladı..."
    )

    for stage in stages:

        await msg.edit(content=stage)

    await msg.edit(
        content=(
            f"✅ {member.mention} "
            f"başarıyla hacklendi."
        )
    )

# ==================================================
# UTILITY
# ==================================================

@bot.command()
async def ping(ctx):

    latency = round(bot.latency * 1000)

    await ctx.send(
        f"🏓 Pong! `{latency}ms`"
    )

@bot.command()
async def avatar(ctx, member: discord.Member=None):

    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member.name} Avatar",
        color=discord.Color.blue()
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
        name="Üye Sayısı",
        value=guild.member_count
    )

    embed.add_field(
        name="Owner",
        value=guild.owner
    )

    if guild.icon:

        embed.set_thumbnail(
            url=guild.icon.url
        )

    await ctx.send(embed=embed)

@bot.command()
async def kullanıcı(
    ctx,
    member: discord.Member=None
):

    member = member or ctx.author

    embed = discord.Embed(
        title=str(member),
        color=discord.Color.purple()
    )

    embed.add_field(
        name="ID",
        value=member.id
    )

    embed.add_field(
        name="Katılım Tarihi",
        value=member.joined_at.strftime(
            "%d/%m/%Y"
        )
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await ctx.send(embed=embed)

@bot.command()
async def botbilgi(ctx):

    embed = discord.Embed(
        title="🤖 Bot Bilgisi",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="Prefix",
        value="."
    )

    embed.add_field(
        name="Sunucu",
        value=len(bot.guilds)
    )

    embed.add_field(
        name="Ping",
        value=f"{round(bot.latency*1000)}ms"
    )

    await ctx.send(embed=embed)

# ==================================================
# BOT BASLAT
# ==================================================

bot.run(TOKEN)
