import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")

ROL_OBJETIVO = "Tsundere"
SONIDO = "I'm not a dere!.mp3"

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):

    if after.channel is None:
        return

    roles = [role.name.lower() for role in member.roles]

    if ROL_OBJETIVO.lower() in roles:

        canal = after.channel

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

bot.run(TOKEN)