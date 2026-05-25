usuarios_activados = set()

from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import asyncio
import os

# Flask para mantener vivo Render
app = Flask('')

@app.route('/')
def home():
    return "Bot vivo"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Token secreto
TOKEN = os.getenv("TOKEN")

# Config
ROL_OBJETIVO = "Tsundere"
SONIDO = "dere.mp3"

# Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):

    # Ignorar mute, cámara, stream, etc
    if before.channel == after.channel:
        return

    # Si salió del VC, resetear activación
    if before.channel is not None and after.channel is None:
        usuarios_activados.discard(member.id)
        return

    # Si no entró a un canal
    if after.channel is None:
        return

    roles = [role.name.lower() for role in member.roles]

    # Verificar rol
    if ROL_OBJETIVO.lower() in roles:

        # Evitar repetir mientras siga dentro
        if member.id in usuarios_activados:
            return

        usuarios_activados.add(member.id)

        canal = after.channel

        # Evitar múltiples conexiones del bot
        if discord.utils.get(bot.voice_clients, guild=member.guild):
            return

        try:
            vc = await canal.connect()

            audio = discord.FFmpegPCMAudio(SONIDO)

            vc.play(audio)

            while vc.is_playing():
                await asyncio.sleep(1)

            await vc.disconnect()

        except Exception as e:
            print("Error:", e)

# Mantener Render vivo
keep_alive()

# Iniciar bot
bot.run(TOKEN)
