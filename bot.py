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

# =========================
# FLASK
# =========================

app = Flask('')

@app.route('/')
def home():
    return "Bot vivo"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("TOKEN")

ROL_OBJETIVO = "Tsundere"
SONIDO = "dere.mp3"

GUILD_ID = 1202033252047794237

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# READY
# =========================

@bot.event
async def on_ready():

    guild = discord.Object(id=GUILD_ID)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands sincronizados: {len(synced)}")

    except Exception as e:
        print(e)

    print(f"Bot conectado como {bot.user}")

# =========================
# /TSUNDERE
# =========================

@bot.tree.command(
    name="tsundere",
    description="Mide el nivel tsundere",
    guild=discord.Object(id=GUILD_ID)
)
async def tsundere(
    interaction: discord.Interaction,
    user: discord.Member
):

    porcentaje = random.randint(0, 100)

    if porcentaje <= 10:
        comentario = "Literalmente una piedra emocional."

    elif porcentaje <= 20:
        comentario = "Frío como servidor de Discord a las 3AM."

    elif porcentaje <= 35:
        comentario = "Tiene leves síntomas de tsunderismo."

    elif porcentaje <= 50:
        comentario = "Tch... empieza a sospecharse algo 💢"

    elif porcentaje <= 65:
        comentario = "Definitivamente oculta sentimientos."

    elif porcentaje <= 80:
        comentario = "Tsundere peligrosa detectada."

    elif porcentaje <= 99:
        comentario = "P-PERO NO ES COMO SI TE QUISIERA O ALGO B-BAKA!!"

    else:
        comentario = "NIVEL MÁXIMO DE TSUNDERISMO ALCANZADO 💢"

    embed = discord.Embed(
        title="💢 Tsundere Meter",
        description=f"{user.mention} es **{porcentaje}% tsundere**",
        color=discord.Color.pink()
    )

    embed.add_field(
        name="Diagnóstico",
        value=comentario,
        inline=False
    )

    if porcentaje == 100:
        embed.set_image(
            url="https://media.tenor.com/images/0b6b5a5d9f6b3c33b3c6fd5a7f5c5a62/tenor.gif"
        )

    await interaction.response.send_message(embed=embed)

# =========================
# /BAKA
# =========================

@bot.tree.command(
    name="baka",
    description="Insulta amistosamente",
    guild=discord.Object(id=GUILD_ID)
)
async def baka(
    interaction: discord.Interaction,
    user: discord.Member
):

    frases = [
        "B-BAKA!! 💢",
        "Tu gameplay preocupa científicamente.",
        "Ni un NPC haría eso.",
        "Tu IQ compite con una tostadora.",
        "Tch... inútil.",
        "Certified clown."
    ]

    frase = random.choice(frases)

    embed = discord.Embed(
        title="💢 Baka Detector",
        description=f"{user.mention}\n\n{frase}",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)

# =========================
# /GD
# =========================

@bot.tree.command(
    name="gd",
    description="Muestra stats de Geometry Dash",
    guild=discord.Object(id=GUILD_ID)
)
async def gd(
    interaction: discord.Interaction,
    username: str
):

    await interaction.response.defer()

    try:

        url = f"https://gdbrowser.com/api/profile/{username}"

        async with aiohttp.ClientSession() as session:

            async with session.get(url) as response:

                if response.status != 200:

                    await interaction.followup.send(
                        "❌ Usuario no encontrado."
                    )
                    return

                data = await response.json()

        estrellas = data.get("stars", 0)
        demons = data.get("demons", 0)
        cp = data.get("cp", 0)
        coins = data.get("coins", 0)
        usercoins = data.get("userCoins", 0)
        rank = data.get("rank", "???")

        embed = discord.Embed(
            title=f"🎮 Geometry Dash Profile",
            description=f"Stats de **{username}**",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="⭐ Stars",
            value=estrellas
        )

        embed.add_field(
            name="😈 Demons",
            value=demons
        )

        embed.add_field(
            name="👑 Creator Points",
            value=cp
        )

        embed.add_field(
            name="🪙 Secret Coins",
            value=coins
        )

        embed.add_field(
            name="💎 User Coins",
            value=usercoins
        )

        embed.add_field(
            name="🏆 Rank",
            value=rank
        )

        comentarios = [
            "wave carried",
            "spaceuk certified",
            "robtop estaría orgulloso",
            "mental illness detected",
            "touch grass difficulty impossible",
            "gd player moment"
        ]

        embed.set_footer(
            text=random.choice(comentarios)
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:

        print(e)

        await interaction.followup.send(
            "❌ Error obteniendo stats de GD."
        )

# =========================
# VOICE EVENT
# =========================

@bot.event
async def on_voice_state_update(member, before, after):

    # Ignorar mute/cámara/stream
    if before.channel == after.channel:
        return

    # Salió del VC
    if before.channel is not None and after.channel is None:

        usuarios_activados.discard(member.id)
        return

    # No entró a VC
    if after.channel is None:
        return

    roles = [role.name.lower() for role in member.roles]

    # Verificar rol
    if ROL_OBJETIVO.lower() not in roles:
        return

    # Evitar repetir
    if member.id in usuarios_activados:
        return

    canal = after.channel

    try:

        usuarios_activados.add(member.id)

        # Limpiar conexiones bug
        if member.guild.voice_client:
            await member.guild.voice_client.disconnect(force=True)

        vc = await canal.connect(reconnect=True)

        audio = discord.FFmpegPCMAudio(SONIDO)

        vc.play(audio)

        while vc.is_playing():
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        await vc.disconnect(force=True)

    except Exception as e:

        print("Error:", e)

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
