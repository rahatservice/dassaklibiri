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
# DATA
# ==================================================

warnings = {}

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
# ERROR
# ==================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("Yetkin yok.")

    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("Üye yok.")

    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("Eksik bilgi.")

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
# HELP MENU
# ==================================================

class HelpSelect(Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="Moderasyon", emoji="🛡️"),
            discord.SelectOption(label="Eğlence", emoji="🎮"),
            discord.SelectOption(label="Utility", emoji="⚙️")
        ]

        super().__init__(
            placeholder="Kategori seç",
            options=options
        )

    async def callback(self, interaction):

        c = self.values[0]

        if c == "Moderasyon":
            txt = ".ban .kick .mute .warn .nuke .rolver"
        elif c == "Eğlence":
            txt = ".zar .iq .8ball .slot"
        else:
            txt = ".ping .avatar .sunucu"

        embed = discord.Embed(
            title=c,
            description=txt,
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(embed=embed)

class HelpView(View):

    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@bot.command()
async def yardım(ctx):

    embed = discord.Embed(
        title="Yardım",
        description="Kategori seç",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed, view=HelpView())

# ==================================================
# MODERASYON
# ==================================================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("Yapamazsın.")

    await member.ban(reason=reason)
    await ctx.send(f"banlandı {member}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="yok"):

    if not await can_moderate(ctx, member):
        return await ctx.send("Yapamazsın.")

    await member.kick(reason=reason)
    await ctx.send(f"kick {member}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, amount: int):

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("silindi", delete_after=2)

# ==================================================
# MUTE SYSTEM
# ==================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")

        for c in ctx.guild.channels:
            await c.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"mute {member}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role in member.roles:
        await member.remove_roles(role)

    await ctx.send(f"unmute {member}")

# ==================================================
# WARN SYSTEM
# ==================================================

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="yok"):

    if member.id not in warnings:
        warnings[member.id] = []

    warnings[member.id].append(reason)

    await ctx.send(f"warn {member}")

@bot.command()
async def warns(ctx, member: discord.Member):

    w = warnings.get(member.id, [])

    await ctx.send("\n".join(w) if w else "warn yok")

# ==================================================
# ROLVER (SMART)
# ==================================================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member_or_role=None, *, role_name=None):

    member = None
    query = None

    if ctx.message.reference:

        msg = await ctx.channel.fetch_message(
            ctx.message.reference.message_id
        )

        member = msg.author
        query = member_or_role

    else:

        if not ctx.message.mentions:
            return await ctx.send("kullanıcı yok")

        member = ctx.message.mentions[0]
        query = role_name

    if not query:
        return await ctx.send("rol yok")

    roles = [r.name for r in ctx.guild.roles]

    match = difflib.get_close_matches(query, roles, n=1, cutoff=0.3)

    if not match:
        return await ctx.send("rol bulunamadı")

    role = discord.utils.get(ctx.guild.roles, name=match[0])

    if role >= ctx.author.top_role:
        return await ctx.send("yetki yok")

    await member.add_roles(role)

    await ctx.send(f"{member} -> {role}")

# ==================================================
# FUN
# ==================================================

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

    await ctx.send(" ".join(r))

# ==================================================
# UTILITY
# ==================================================

@bot.command()
async def ping(ctx):

    await ctx.send(f"{round(bot.latency*1000)}ms")

@bot.command()
async def avatar(ctx, member: discord.Member=None):

    member = member or ctx.author

    embed = discord.Embed()
    embed.set_image(url=member.display_avatar.url)

    await ctx.send(embed=embed)

# ==================================================
# NUKE
# ==================================================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):

    ch = ctx.channel
    new = await ch.clone()
    await ch.delete()

    await new.send("boom")

# ==================================================
# BOT START
# ==================================================

bot.run(TOKEN)
