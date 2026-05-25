usuarios_activados = set()

from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import random

# =========================
# FLASK PARA RENDER
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

# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Bot conectado como {bot.user}")

# =========================
# SLASH COMMANDS
# =========================

@bot.tree.command(
    name="tsundere",
    description="Mide el nivel tsundere de alguien"
)
async def tsundere(
    interaction: discord.Interaction,
    user: discord.Member
):

    porcentaje = random.randint(0, 100)

    frases = [
        "P-pero no es como si me gustaras o algo... b-baka!",
        "N-no te confundas!",
        "Hmph... supongo que eres algo tsundere.",
        "No creas que hice esto por ti 💢",
        "Tch... qué molesto eres."
    ]

    frase = random.choice(frases)

    embed = discord.Embed(
        title="💢 Tsundere Meter",
        description=f"{user.mention} es **{porcentaje}% tsundere**",
        color=discord.Color.pink()
    )

    embed.add_field(
        name="Diagnóstico",
        value=frase,
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# =========================
# VOICE EVENT
# =========================

@bot.event
async def on_voice_state_update(member, before, after):

    # Ignorar mute/cámara/stream
    if before.channel == after.channel:
        return

    # Si salió del VC
    if before.channel is not None and after.channel is None:

        if member.id in usuarios_activados:
            usuarios_activados.remove(member.id)

        return

    # Si no entró a canal
    if after.channel is None:
        return

    roles = [role.name.lower() for role in member.roles]

    # Verificar rol
    if ROL_OBJETIVO.lower() not in roles:
        return

    # Evitar repetir mientras siga dentro
    if member.id in usuarios_activados:
        return

    canal = after.channel

    try:

        # Marcar usuario
        usuarios_activados.add(member.id)

        # Conectar
        vc = await canal.connect(reconnect=True)

        # Audio
        audio = discord.FFmpegPCMAudio(SONIDO)

        vc.play(audio)

        # Esperar a que termine REALMENTE
        while vc.is_playing():
            await asyncio.sleep(1)

        # Esperita extra anti-bug
        await asyncio.sleep(1)

        # Desconectar
        await vc.disconnect(force=True)

    except Exception as e:

        print("Error:", e)

        # Limpiar conexión bugueada
        try:
            if member.guild.voice_client:
                await member.guild.voice_client.disconnect(force=True)
        except:
            pass

        # Permitir reactivación
        if member.id in usuarios_activados:
            usuarios_activados.remove(member.id)

# =========================
# START
# =========================

keep_alive()
bot.run(TOKEN)
