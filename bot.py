usuarios_activados = set()

from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import random
import aiohttp
from datetime import datetime, timezone
import re

# =========================
# FLASK (keep-alive)
# =========================

app = Flask('')

@app.route('/')
def home():
    return "Bot vivo"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# =========================
# CONFIG
# =========================

TOKEN    = os.getenv("TOKEN")
ROL_OBJETIVO = "Tsundere"
SONIDO   = "dere.mp3"
GUILD_ID = 1202033252047794237

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.voice_states    = True
intents.members         = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Helper: guild object
GUILD = discord.Object(id=GUILD_ID)

# =========================
# READY
# =========================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=GUILD)
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error sincronizando comandos: {e}")
    print(f"Bot conectado como {bot.user}")

# =========================
# ERROR HANDLER GLOBAL
# =========================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Calma. Podés usar esto de nuevo en **{error.retry_after:.1f}s**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ Error: `{error}`", ephemeral=True
        )
        print(f"Error en comando: {error}")

# =========================
# /TSUNDERE
# =========================

@bot.tree.command(
    name="tsundere",
    description="Mide el nivel tsundere de alguien",
    guild=GUILD
)
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
async def tsundere(interaction: discord.Interaction, user: discord.Member):

    porcentaje = random.randint(0, 100)

    niveles = [
        (10,  "Literalmente una piedra emocional."),
        (20,  "Frío como servidor de Discord a las 3AM."),
        (35,  "Tiene leves síntomas de tsunderismo."),
        (50,  "Tch... empieza a sospecharse algo 💢"),
        (65,  "Definitivamente oculta sentimientos."),
        (80,  "Tsundere peligrosa detectada."),
        (99,  "P-PERO NO ES COMO SI TE QUISIERA O ALGO B-BAKA!!"),
        (100, "NIVEL MÁXIMO DE TSUNDERISMO ALCANZADO 💢"),
    ]

    comentario = next(c for tope, c in niveles if porcentaje <= tope)

    embed = discord.Embed(
        title="💢 Tsundere Meter",
        description=f"{user.mention} es **{porcentaje}% tsundere**",
        color=discord.Color.pink()
    )
    embed.add_field(name="Diagnóstico", value=comentario, inline=False)

    barra = "█" * (porcentaje // 10) + "░" * (10 - porcentaje // 10)
    embed.add_field(name="Nivel", value=f"`[{barra}] {porcentaje}%`", inline=False)

    await interaction.response.send_message(embed=embed)

# =========================
# /GD
# =========================

@bot.tree.command(
    name="gd",
    description="Muestra stats de Geometry Dash de un usuario",
    guild=GUILD
)
@app_commands.checks.cooldown(1, 8, key=lambda i: (i.guild_id, i.user.id))
async def gd(interaction: discord.Interaction, username: str):

    await interaction.response.defer()

    try:
        url = f"https://gdbrowser.com/api/profile/{username}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    await interaction.followup.send("❌ Usuario no encontrado en GD.")
                    return
                data = await response.json(content_type=None)

        campos = [
            ("⭐ Stars",          data.get("stars", 0)),
            ("🌙 Moons",          data.get("moons", 0)),
            ("😈 Demons",         data.get("demons", 0)),
            ("👑 Creator Points", data.get("cp", 0)),
            ("🪙 Secret Coins",   data.get("coins", 0)),
            ("💎 User Coins",     data.get("userCoins", 0)),
            ("🏆 Global Rank",    data.get("rank", "???") or "Sin rankear"),
        ]

        embed = discord.Embed(
            title="🎮 Geometry Dash Profile",
            description=f"Stats de **{username}**",
            color=discord.Color.orange()
        )

        for nombre, valor in campos:
            embed.add_field(name=nombre, value=f"`{valor}`")

        frases = [
            "wave carried",
            "spaceuk certified",
            "robtop estaría orgulloso",
            "mental illness detected",
            "touch grass difficulty: impossible",
            "gd player moment",
            "geometry dash never",
        ]
        embed.set_footer(text=random.choice(frases))

        await interaction.followup.send(embed=embed)

    except asyncio.TimeoutError:
        await interaction.followup.send("❌ GDBrowser tardó demasiado. Intentá de nuevo.")
    except Exception as e:
        print(e)
        await interaction.followup.send("❌ Error obteniendo stats de GD.")

# =========================
# /USERINFO
# =========================

@bot.tree.command(
    name="userinfo",
    description="Info detallada de un miembro del servidor",
    guild=GUILD
)
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user

    created  = discord.utils.format_dt(user.created_at, "R")
    joined   = discord.utils.format_dt(user.joined_at, "R") if user.joined_at else "Desconocido"
    roles    = [r.mention for r in user.roles if r.name != "@everyone"]
    top_role = user.top_role.mention if user.top_role.name != "@everyone" else "Ninguno"

    embed = discord.Embed(
        title=f"👤 {user.display_name}",
        color=user.color if user.color.value else discord.Color.blurple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Tag",           value=str(user),                       inline=True)
    embed.add_field(name="ID",            value=f"`{user.id}`",                  inline=True)
    embed.add_field(name="Cuenta creada", value=created,                         inline=True)
    embed.add_field(name="Entró al servidor", value=joined,                      inline=True)
    embed.add_field(name="Rol principal", value=top_role,                        inline=True)
    embed.add_field(name="Bot",           value="Sí" if user.bot else "No",      inline=True)

    if roles:
        roles_str = " ".join(roles[:15])
        if len(roles) > 15:
            roles_str += f" (+{len(roles) - 15} más)"
        embed.add_field(name=f"Roles ({len(roles)})", value=roles_str, inline=False)

    await interaction.response.send_message(embed=embed)

# =========================
# /AVATAR
# =========================

@bot.tree.command(
    name="avatar",
    description="Muestra el avatar de alguien en full size",
    guild=GUILD
)
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user

    embed = discord.Embed(
        title=f"🖼️ Avatar de {user.display_name}",
        color=discord.Color.blurple()
    )

    formats = []
    for fmt in ["png", "jpg", "webp"]:
        formats.append(f"[{fmt.upper()}]({user.display_avatar.with_format(fmt).url})")
    if user.display_avatar.is_animated():
        formats.append(f"[GIF]({user.display_avatar.with_format('gif').url})")

    embed.set_image(url=user.display_avatar.url)
    embed.set_footer(text=" | ".join(formats))

    await interaction.response.send_message(embed=embed)

# =========================
# /SERVERINFO
# =========================

@bot.tree.command(
    name="serverinfo",
    description="Info y estadísticas del servidor",
    guild=GUILD
)
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    total    = guild.member_count
    bots     = sum(1 for m in guild.members if m.bot)
    humanos  = total - bots
    online   = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)

    texto   = sum(1 for c in guild.channels if isinstance(c, discord.TextChannel))
    voz     = sum(1 for c in guild.channels if isinstance(c, discord.VoiceChannel))
    foros   = sum(1 for c in guild.channels if isinstance(c, discord.ForumChannel))

    created = discord.utils.format_dt(guild.created_at, "D")

    embed = discord.Embed(
        title=f"🏠 {guild.name}",
        color=discord.Color.blurple()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="👥 Miembros",   value=f"`{humanos}` humanos · `{bots}` bots", inline=True)
    embed.add_field(name="🟢 Online",     value=f"`{online}`",                           inline=True)
    embed.add_field(name="📅 Creado",     value=created,                                 inline=True)
    embed.add_field(name="💬 Texto",      value=f"`{texto}`",                            inline=True)
    embed.add_field(name="🔊 Voz",        value=f"`{voz}`",                              inline=True)
    embed.add_field(name="📋 Foros",      value=f"`{foros}`",                            inline=True)
    embed.add_field(name="🎭 Roles",      value=f"`{len(guild.roles)}`",                 inline=True)
    embed.add_field(name="😄 Emojis",     value=f"`{len(guild.emojis)}`",                inline=True)
    embed.add_field(name="🆔 Server ID",  value=f"`{guild.id}`",                         inline=True)

    if guild.owner:
        embed.set_footer(text=f"Owner: {guild.owner.display_name}")

    await interaction.response.send_message(embed=embed)

# =========================
# /POLL
# =========================

@bot.tree.command(
    name="poll",
    description="Crea una encuesta rápida con dos opciones",
    guild=GUILD
)
@app_commands.describe(
    pregunta="¿Qué querés preguntar?",
    opcion_a="Primera opción",
    opcion_b="Segunda opción",
    opcion_c="Tercera opción (opcional)",
    opcion_d="Cuarta opción (opcional)"
)
async def poll(
    interaction: discord.Interaction,
    pregunta: str,
    opcion_a: str,
    opcion_b: str,
    opcion_c: str = None,
    opcion_d: str = None
):
    emojis  = ["🇦", "🇧", "🇨", "🇩"]
    opciones = [opcion_a, opcion_b, opcion_c, opcion_d]
    opciones = [(e, o) for e, o in zip(emojis, opciones) if o]

    descripcion = "\n".join(f"{e} {o}" for e, o in opciones)

    embed = discord.Embed(
        title=f"📊 {pregunta}",
        description=descripcion,
        color=discord.Color.yellow()
    )
    embed.set_footer(text=f"Encuesta creada por {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    for emoji, _ in opciones:
        await msg.add_reaction(emoji)

# =========================
# /RECORDAR
# =========================

@bot.tree.command(
    name="recordar",
    description="Te manda un DM recordatorio después de X minutos",
    guild=GUILD
)
@app_commands.describe(
    minutos="Cuántos minutos esperar (máx 1440)",
    mensaje="Qué recordarte"
)
async def recordar(interaction: discord.Interaction, minutos: int, mensaje: str):
    if minutos < 1 or minutos > 1440:
        await interaction.response.send_message("❌ Usá entre 1 y 1440 minutos (24hs).", ephemeral=True)
        return

    await interaction.response.send_message(
        f"✅ Te aviso en **{minutos} minuto{'s' if minutos != 1 else ''}**. No te olvides de tener los DMs abiertos.",
        ephemeral=True
    )

    async def mandar_recordatorio():
        await asyncio.sleep(minutos * 60)
        try:
            embed = discord.Embed(
                title="⏰ Recordatorio",
                description=mensaje,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Lo pediste en #{interaction.channel.name}")
            await interaction.user.send(embed=embed)
        except discord.Forbidden:
            pass

    asyncio.create_task(mandar_recordatorio())

# =========================
# /DICE
# =========================

@bot.tree.command(
    name="dice",
    description="Tira dados. Formato: 2d6, 1d20, 3d8...",
    guild=GUILD
)
@app_commands.describe(tirada="Formato XdY — ej: 2d6, 1d20, 4d4")
async def dice(interaction: discord.Interaction, tirada: str):
    match = re.fullmatch(r"(\d+)d(\d+)", tirada.lower().strip())
    if not match:
        await interaction.response.send_message("❌ Formato inválido. Usá algo como `2d6` o `1d20`.", ephemeral=True)
        return

    cantidad = int(match.group(1))
    caras    = int(match.group(2))

    if cantidad < 1 or cantidad > 30:
        await interaction.response.send_message("❌ Máximo 30 dados a la vez.", ephemeral=True)
        return
    if caras < 2 or caras > 1000:
        await interaction.response.send_message("❌ Los dados deben tener entre 2 y 1000 caras.", ephemeral=True)
        return

    resultados = [random.randint(1, caras) for _ in range(cantidad)]
    total      = sum(resultados)
    detalle    = " + ".join(f"`{r}`" for r in resultados)

    embed = discord.Embed(
        title=f"🎲 {tirada.upper()}",
        color=discord.Color.purple()
    )
    if cantidad > 1:
        embed.add_field(name="Dados", value=detalle, inline=False)
    embed.add_field(name="Total", value=f"**{total}**", inline=False)

    # Comentario si saca máximo o mínimo
    if all(r == caras for r in resultados):
        embed.set_footer(text="🔥 Todos al máximo. Literal.")
    elif all(r == 1 for r in resultados):
        embed.set_footer(text="💀 Todo al mínimo. Condolencias.")

    await interaction.response.send_message(embed=embed)

# =========================
# WEBHOOK LOGGER (GD completions)
# =========================

@bot.event
async def on_message(message):
    if not message.webhook_id or not message.content:
        return

    contenido = message.content.lower()

    if "completed" in contenido:
        dificultad = "😈 Demon"
        if "extreme"      in contenido: dificultad = "🔥 Extreme Demon"
        elif "insane"     in contenido: dificultad = "💀 Insane Demon"
        elif "hard demon" in contenido: dificultad = "👹 Hard Demon"
        elif "medium"     in contenido: dificultad = "😵 Medium Demon"
        elif "easy"       in contenido: dificultad = "😌 Easy Demon"

        frases = [
            "P-pero no es como si estuviera impresionada o algo... b-baka!",
            "Mental illness detected.",
            "wave carried.",
            "touch grass difficulty: impossible.",
            "gd player moment.",
            "robtop is watching.",
            "human sanity no longer detected.",
        ]

        embed = discord.Embed(
            title="😈 DEMON COMPLETED",
            description=message.content,
            color=discord.Color.red()
        )
        embed.add_field(name="Difficulty",       value=dificultad,              inline=False)
        embed.add_field(name="Tsundere Comment", value=random.choice(frases),   inline=False)

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await message.channel.send(embed=embed)

    elif "new best" in contenido:
        # Intentar extraer porcentaje del texto
        porcentaje_match = re.search(r"(\d+)%", message.content)
        porcentaje_str = porcentaje_match.group(0) if porcentaje_match else "??%"

        frases = [
            f"SO CLOSE 💀 ({porcentaje_str})",
            "pain.",
            "mental destruction complete.",
            "robtop laughed at this.",
            f"{porcentaje_str} incident detected.",
        ]

        embed = discord.Embed(
            title="🔥 NEW BEST",
            description=message.content,
            color=discord.Color.orange()
        )
        embed.add_field(name="Comment", value=random.choice(frases), inline=False)

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        await message.channel.send(embed=embed)

# =========================
# VOICE EVENT (tsundere sound)
# =========================

@bot.event
async def on_voice_state_update(member, before, after):
    # Ignorar mute/cámara/deafen
    if before.channel == after.channel:
        return

    # Salió
    if after.channel is None:
        usuarios_activados.discard(member.id)
        return

    roles = {role.name.lower() for role in member.roles}
    if ROL_OBJETIVO.lower() not in roles:
        return
    if member.id in usuarios_activados:
        return

    canal = after.channel

    try:
        usuarios_activados.add(member.id)

        # Desconectar si ya hay vc activo
        if member.guild.voice_client:
            await member.guild.voice_client.disconnect(force=True)
            await asyncio.sleep(0.5)

        vc = await canal.connect(reconnect=True)

        if not os.path.exists(SONIDO):
            print(f"Archivo {SONIDO} no encontrado.")
            await vc.disconnect(force=True)
            usuarios_activados.discard(member.id)
            return

        vc.play(discord.FFmpegPCMAudio(SONIDO))

        while vc.is_playing():
            await asyncio.sleep(1)

        await asyncio.sleep(0.5)
        await vc.disconnect(force=True)

    except Exception as e:
        print(f"Error en voice event: {e}")
        usuarios_activados.discard(member.id)
        try:
            if member.guild.voice_client:
                await member.guild.voice_client.disconnect(force=True)
        except:
            pass

# =========================
# START
# =========================

keep_alive()
bot.run(TOKEN)
