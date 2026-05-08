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

# =========================
# DATA
# =========================

warnings = {}

# =========================
# READY
# =========================

@bot.event
async def on_ready():
    print(f"{bot.user} aktif")
    await bot.change_presence(activity=discord.Game(".yardım"))

# =========================
# ERROR
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("❌ Yetkin yok.")

    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("❌ Üye bulunamadı.")

    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("❌ Eksik bilgi.")

# =========================
# PERMISSION CHECK
# =========================

async def can_moderate(ctx, member):

    if member == ctx.author:
        return False

    if member.top_role >= ctx.author.top_role:
        return False

    if member.top_role >= ctx.guild.me.top_role:
        return False

    return True

# =========================
# HELP MENU
# =========================

class HelpSelect(Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Moderasyon", emoji="🛡️"),
            discord.SelectOption(label="Eğlence", emoji="🎮"),
            discord.SelectOption(label="Utility", emoji="⚙️")
        ]

        super().__init__(placeholder="Kategori seç", options=options)

    async def callback(self, interaction):

        c = self.values[0]

        if c == "Moderasyon":
            txt = """
`.ban` `.kick` `.mute` `.unmute`
`.warn` `.warns` `.clear`
`.rolver` `.rolal` `.nuke`
"""

            color = discord.Color.red()

        elif c == "Eğlence":
            txt = """
`.zar` `.iq` `.8ball`
`.slot` `.ship` `.öp`
`.tokat` `.hackle`
"""

            color = discord.Color.purple()

        else:
            txt = """
`.ping` `.avatar`
`.sunucu` `.kullanıcı`
`.botbilgi`
"""

            color = discord.Color.green()

        embed = discord.Embed(
            title=f"{c} Komutları",
            description=txt,
            color=color
        )

        await interaction.response.edit_message(embed=embed)

class HelpView(View):

    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="🤖 BOT YARDIM",
        description="Kategori seç ve komutları gör",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=embed, view=HelpView())

# =========================
# MODERATION
# =========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("❌ Yapamazsın")

    await member.ban(reason=reason)
    await ctx.send(f"🔨 ban: {member}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("❌ Yapamazsın")

    await member.kick(reason=reason)
    await ctx.send(f"👢 kick: {member}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} silindi", delete_after=2)

# =========================
# MUTE SYSTEM
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")

        for ch in ctx.guild.channels:
            await ch.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 mute {member}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role in member.roles:
        await member.remove_roles(role)

    await ctx.send(f"🔊 unmute {member}")

# =========================
# WARN SYSTEM
# =========================

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="yok"):

    if member.id not in warnings:
        warnings[member.id] = []

    warnings[member.id].append(reason)

    await ctx.send(f"⚠️ warn {member}")

@bot.command()
async def warns(ctx, member: discord.Member):

    w = warnings.get(member.id, [])

    await ctx.send("\n".join(w) if w else "warn yok")

# =========================
# SMART ROLVER
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member_or_role=None, *, role_name=None):

    member = None
    query = None

    if ctx.message.reference:

        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        member = msg.author
        query = member_or_role

    else:

        if not ctx.message.mentions:
            return await ctx.send("kullanıcı yok")

        member = ctx.message.mentions[0]
        query = role_name

    roles = [r.name for r in ctx.guild.roles]

    match = difflib.get_close_matches(query, roles, n=1, cutoff=0.3)

    if not match:
        return await ctx.send("rol yok")

    role = discord.utils.get(ctx.guild.roles, name=match[0])

    if role >= ctx.author.top_role:
        return await ctx.send("yetki yok")

    await member.add_roles(role)

    await ctx.send(f"✅ {member} → {role}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, *, role: discord.Role):

    if role >= ctx.author.top_role:
        return await ctx.send("yetki yok")

    await member.remove_roles(role)

    await ctx.send(f"❌ rol alındı")

# =========================
# FUN
# =========================

@bot.command()
async def zar(ctx):
    await ctx.send(random.randint(1,6))

@bot.command()
async def iq(ctx, member: discord.Member=None):

    member = member or ctx.author
    await ctx.send(random.randint(1,300))

@bot.command(name="8ball")
async def ball(ctx, *, q):
    await ctx.send(random.choice(["evet","hayır","belki"]))

@bot.command()
async def slot(ctx):

    e = ["🍎","🍌","🍇"]

    r = [random.choice(e) for _ in range(3)]

    await ctx.send(" | ".join(r))

@bot.command()
async def ship(ctx, a: discord.Member, b: discord.Member):
    await ctx.send(f"%{random.randint(1,100)}")

@bot.command()
async def öp(ctx, member: discord.Member):
    await ctx.send(f"😘 {member}")

@bot.command()
async def tokat(ctx, member: discord.Member):
    await ctx.send(f"👋 {member}")

@bot.command()
async def hackle(ctx, member: discord.Member):

    steps = ["IP...", "hack...", "done"]

    msg = await ctx.send("başladı")

    for s in steps:
        await msg.edit(content=s)

    await msg.edit(content=f"{member} hacklendi 💀")

# =========================
# UTILITY
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency*1000)}ms")

@bot.command()
async def avatar(ctx, member: discord.Member=None):

    member = member or ctx.author

    e = discord.Embed()
    e.set_image(url=member.display_avatar.url)

    await ctx.send(embed=e)

@bot.command()
async def sunucu(ctx):

    g = ctx.guild

    e = discord.Embed(title=g.name)
    e.add_field(name="Üye", value=g.member_count)

    await ctx.send(embed=e)

@bot.command()
async def kullanıcı(ctx, member: discord.Member=None):

    member = member or ctx.author

    e = discord.Embed(title=str(member))
    e.add_field(name="ID", value=member.id)

    await ctx.send(embed=e)

@bot.command()
async def botbilgi(ctx):
    await ctx.send(f"Guild: {len(bot.guilds)}")

# =========================
# NUKE
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):

    ch = ctx.channel
    new = await ch.clone()
    await ch.delete()

    await new.send("💥 reset")

# =========================
# RUN
# =========================

bot.run(TOKEN)
