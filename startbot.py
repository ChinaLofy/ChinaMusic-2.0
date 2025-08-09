import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import platform
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='c!', intents=intents, help_command=None)
        
        if platform.system() == "Windows":
            self.FFMPEG_PATH = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe')
        else:
            self.FFMPEG_PATH = "ffmpeg"
            
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -bufsize 512k',
        }
        
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("Autenticação com Spotify bem-sucedida.")
        except Exception as e:
            self.sp = None
            print(f"ERRO de autenticação com Spotify: {e}")

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        try:
            synced = await self.tree.sync()
            print(f"Sincronizei {len(synced)} comando(s) de barra.")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")

    async def on_ready(self):
        print("-" * 50)
        print(f'Bot conectado como {self.user}')
        print(f"O bot está pronto para usar!")
        print(f"Use {self.command_prefix}help para ver os comandos.")
        print("-" * 50)

async def main():
    bot = MyBot()
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
        print("ERRO: DISCORD_TOKEN não encontrado no arquivo .env.")
        return
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())