import os
import random
import discord
from discord.ext import commands
from datetime import timedelta
from discord.ui import View, Select

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
# HATA SISTEMI
# ==================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("Bunun için yetkin yok.")

    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("Eksik argüman girdin.")

    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("Üye bulunamadı.")

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

class HelpMenu(Select):

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

        category = self.values[0]

        if category == "Moderasyon":

            text = """
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

        elif category == "Eğlence":

            text = """
`.zar`
`.yazitura`
`.iq`
`.8ball`
`.slot`
`.ship`
"""

        else:

            text = """
`.ping`
`.avatar`
`.sunucu`
`.kullanıcı`
`.botbilgi`
"""

        embed = discord.Embed(
            title=f"{category} Komutları",
            description=text,
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed
        )

class HelpView(View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpMenu())

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
        return await ctx.send("Bu kişiyi banlayamazsın.")

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
        return await ctx.send("Bu kişiyi kickleyemezsin.")

    await member.kick(reason=reason)

    embed = discord.Embed(
        title="👢 Kicklendi",
        description=f"{member.mention} kicklendi.\nSebep: {reason}",
        color=discord.Color.orange()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, dakika: int, *, reason="Sebep belirtilmedi"):

    if not await can_moderate(ctx, member):
        return await ctx.send("Bu kişiye timeout atamazsın.")

    duration = timedelta(minutes=dakika)

    await member.timeout(
        duration,
        reason=reason
    )

    embed = discord.Embed(
        title="⏳ Timeout",
        description=f"{member.mention} {dakika} dakika susturuldu.",
        color=discord.Color.yellow()
    )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):

    await member.timeout(None)

    await ctx.send(f"{member.mention} timeout kaldırıldı.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, amount: int):

    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(f"{amount} mesaj silindi.")

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

    await ctx.send(f"Slowmode {seconds} saniye oldu.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, *, role: discord.Role):

    if role >= ctx.author.top_role:
        return await ctx.send("Bu rolü veremezsin.")

    await member.add_roles(role)

    await ctx.send(f"{member.mention} kişisine {role.name} verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, *, role: discord.Role):

    if role >= ctx.author.top_role:
        return await ctx.send("Bu rolü alamazsın.")

    await member.remove_roles(role)

    await ctx.send(f"{member.mention} kişisinden {role.name} alındı.")

# ==================================================
# EGLENCE
# ==================================================

@bot.command()
async def zar(ctx):

    await ctx.send(f"🎲 Zar sonucu: {random.randint(1,6)}")

@bot.command()
async def yazitura(ctx):

    await ctx.send(random.choice([
        "Yazı",
        "Tura"
    ]))

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

    await ctx.send(random.choice(answers))

@bot.command()
async def slot(ctx):

    emojis = ["🍎", "🍌", "🍇", "💎"]

    result = [
        random.choice(emojis),
        random.choice(emojis),
        random.choice(emojis)
    ]

    text = " | ".join(result)

    if len(set(result)) == 1:
        await ctx.send(f"{text}\nKazandın!")
    else:
        await ctx.send(f"{text}\nKaybettin!")

@bot.command()
async def ship(ctx, member1: discord.Member, member2: discord.Member):

    percent = random.randint(1,100)

    await ctx.send(
        f"❤️ {member1.name} + {member2.name} = %{percent}"
    )

# ==================================================
# UTILITY
# ==================================================

@bot.command()
async def ping(ctx):

    latency = round(bot.latency * 1000)

    await ctx.send(f"🏓 Pong! `{latency}ms`")

@bot.command()
async def avatar(ctx, member: discord.Member=None):

    member = member or ctx.author

    embed = discord.Embed(
        title=f"{member.name} Avatar"
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
        color=discord.Color.blue()
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
async def kullanıcı(ctx, member: discord.Member=None):

    member = member or ctx.author

    embed = discord.Embed(
        title=str(member),
        color=discord.Color.green()
    )

    embed.add_field(
        name="ID",
        value=member.id
    )

    embed.add_field(
        name="Katılım",
        value=member.joined_at.strftime("%d/%m/%Y")
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await ctx.send(embed=embed)

@bot.command()
async def botbilgi(ctx):

    embed = discord.Embed(
        title="🤖 Bot Bilgisi",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Prefix",
        value="."
    )

    embed.add_field(
        name="Ping",
        value=f"{round(bot.latency*1000)}ms"
    )

    embed.add_field(
        name="Sunucu",
        value=len(bot.guilds)
    )

    await ctx.send(embed=embed)

# ==================================================
# EXTRA KOMUTLAR
# ==================================================

@bot.command()
async def öp(ctx, member: discord.Member):

    await ctx.send(
        f"😘 {ctx.author.mention} {member.mention} kişisini öptü."
    )

@bot.command()
async def tokat(ctx, member: discord.Member):

    await ctx.send(
        f"👋 {ctx.author.mention} {member.mention} kişisine tokat attı."
    )

@bot.command()
async def hackle(ctx, member: discord.Member):

    messages = [
        "IP bulunuyor...",
        "Discord tokeni alınıyor...",
        "Annesinin kızlık soyadı bulunuyor...",
        "Minecraft hesabı çalınıyor..."
    ]

    msg = await ctx.send("Hack başlatıldı...")

    for m in messages:
        await msg.edit(content=m)

    await msg.edit(
        content=f"✅ {member.mention} başarıyla hacklendi."
    )

# ==================================================
# BOT BASLAT
# ==================================================

bot.run(TOKEN)
