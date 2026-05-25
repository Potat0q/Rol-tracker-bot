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

# PONÉ TU ID DEL SERVER ACÁ
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

    guild = discord.Object(id=1202033252047794237)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands sincronizados: {len(synced)}")

    except Exception as e:
        print(e)

    print(f"Bot conectado como {bot.user}")

# =========================
# SLASH COMMAND
# =========================

@bot.tree.command(
    name="tsundere",
    description="Mide el nivel tsundere",
    guild=discord.Object(id=1202033252047794237)
)
async def tsundere(
    interaction: discord.Interaction,
    user: discord.Member
):

    porcentaje = random.randint(0, 100)

    frases = [
        "P-pero no es como si me gustaras o algo... b-baka!",
        "N-no te confundas!",
        "Tch... qué molesto eres 💢",
        "Hmph...",
        "No creas que hice esto por ti."
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

        usuarios_activados.discard(member.id)
        return

    # Si no entró a VC
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

        # Desconectar conexiones bugueadas
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
