# cogs/music.py

import discord
from discord.ext import commands
import yt_dlp
import asyncio
import re
import spotipy

def search_and_extract_info(query: str, sp: spotipy.Spotify):
    youtube_playlist_match = re.match(r'(https?://)?(www\.)?youtube\.com/playlist\?list=([\w-]+)', query)
    spotify_url_match = re.match(r'https?://open\.spotify\.com/(track|playlist|album)/([\w-]+)', query)

    if spotify_url_match and sp:
        url_type = spotify_url_match.group(1)
        url_id = spotify_url_match.group(2)
        song_list = []
        try:
            if url_type == 'track':
                track = sp.track(url_id)
                search_query = f"{track['name']} {track['artists'][0]['name']} audio"
                return search_and_extract_info(search_query, sp)
            elif url_type == 'playlist' or url_type == 'album':
                results = sp.playlist_tracks(url_id) if url_type == 'playlist' else sp.album_tracks(url_id)
                for item in results['items']:
                    track_item = item.get('track')
                    if track_item and track_item['artists']:
                        title = track_item['name']
                        artist = track_item['artists'][0]['name']
                        song_list.append({
                            'title': f"{title} - {artist}",
                            'page_url': f"ytsearch:{title} {artist}"
                        })
                return song_list, 'playlist'
        except Exception as e:
            print(f"Erro ao processar link do Spotify: {e}")
            return None, None
    
    YTDL_OPTIONS = {
        'format': 'bestaudio', 'default_search': 'ytsearch', 'quiet': True, 'ignoreerrors': True
    }
    if youtube_playlist_match:
        YTDL_OPTIONS['extract_flat'] = 'in_playlist'
        YTDL_OPTIONS['noplaylist'] = False
    else:
        YTDL_OPTIONS['noplaylist'] = True

    try:
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)
            song_list = []
            if not info: return None, None
            if 'entries' in info and len(info['entries']) > 0:
                for entry in info['entries']:
                    if entry:
                        song_list.append({
                            'page_url': entry.get('webpage_url', entry.get('url')),
                            'title': entry.get('title', 'Título Desconhecido')
                        })
                return song_list, 'playlist' if len(song_list) > 1 else 'song'
            else:
                song_list.append({
                    'page_url': info.get('webpage_url', info.get('url')),
                    'title': info.get('title', 'Título Desconhecido')
                })
                return song_list, 'song'
    except Exception as e:
        print(f"[ERRO] Falha ao buscar com yt_dlp: {e}")
        return None, None

class MusicCog(commands.Cog, name="Música"):
    def __init__(self, bot):
        self.bot = bot
        self.sp = bot.sp
        self.queues = {}
        self.history = {}
        self.current_song = {}
        self.guild_volumes = {}
        self.FFMPEG_PATH = bot.FFMPEG_PATH
        self.FFMPEG_OPTIONS = bot.FFMPEG_OPTIONS

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog de Música carregado.")

    async def play_next(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        voice_client = ctx.guild.voice_client
        if voice_client and guild_id in self.queues and self.queues[guild_id]:
            if guild_id in self.current_song and self.current_song[guild_id]:
                if guild_id not in self.history: self.history[guild_id] = []
                self.history[guild_id].append(self.current_song[guild_id])
            
            song_info = self.queues[guild_id].pop(0)
            self.current_song[guild_id] = song_info
            page_url_or_search = song_info['page_url']
            title = song_info['title']
            YTDL_STREAM_OPTIONS = {
                'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch'
            }
            loading_message = await ctx.send(embed=discord.Embed(description=f"⏳ Carregando **{title}**...", color=discord.Color.yellow()))
            try:
                with yt_dlp.YoutubeDL(YTDL_STREAM_OPTIONS) as ydl:
                    stream_info = ydl.extract_info(page_url_or_search, download=False)
                    if 'entries' in stream_info: stream_info = stream_info['entries'][0]
                    stream_url = stream_info['url']
                    final_title = stream_info.get('title', title)
                    self.current_song[guild_id]['title'] = final_title
                
                volume = self.guild_volumes.get(guild_id, 0.5)
                audio_source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(stream_url, executable=self.FFMPEG_PATH, **self.FFMPEG_OPTIONS),
                    volume=volume
                )
                voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                embed = discord.Embed(title="▶️ Tocando Agora", description=f"**{final_title}**", color=discord.Color.blue())
                await loading_message.edit(embed=embed)
            except Exception as e:
                print(f"Erro ao tocar '{title}': {e}")
                await loading_message.edit(embed=discord.Embed(title="❌ Erro ao Tocar", description=f"Não foi possível tocar **{title}**. Pulando...", color=discord.Color.dark_red()))
                await self.play_next(ctx)
        else:
            self.current_song[ctx.guild.id] = None

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx: commands.Context, *, query: str):
        if not ctx.author.voice:
            await ctx.send(embed=discord.Embed(description="Você precisa estar em um canal de voz!", color=discord.Color.orange()))
            return
        
        voice_client = ctx.guild.voice_client
        if voice_client is None: await ctx.author.voice.channel.connect()
        else: await voice_client.move_to(ctx.author.voice.channel)
            
        guild_id = ctx.guild.id
        if guild_id not in self.queues: self.queues[guild_id] = []
        
        msg = await ctx.send(embed=discord.Embed(description='🔎 Processando seu pedido...', color=discord.Color.yellow()))
        
        songs_to_add, result_type = await self.bot.loop.run_in_executor(None, search_and_extract_info, query, self.sp)
        
        if songs_to_add:
            self.queues[guild_id].extend(songs_to_add)
            if result_type == 'playlist': await msg.edit(embed=discord.Embed(description=f"✅ Playlist com **{len(songs_to_add)}** músicas adicionada à fila!", color=discord.Color.green()))
            else: await msg.edit(embed=discord.Embed(description=f"🎵 **{songs_to_add[0]['title']}** adicionado à fila.", color=discord.Color.green()))
        else:
            await msg.edit(embed=discord.Embed(description="❌ Não encontrei resultados.", color=discord.Color.red()))
            return
            
        if not ctx.guild.voice_client.is_playing() and not ctx.guild.voice_client.is_paused():
            await self.play_next(ctx)
    
    @commands.command(name='pause')
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send(embed=discord.Embed(description="⏸️ Música pausada.", color=discord.Color.orange()))

    @commands.command(name='resume')
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send(embed=discord.Embed(description="▶️ Música retomada.", color=discord.Color.green()))

    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_connected():
            guild_id = ctx.guild.id
            self.queues[guild_id] = []
            if guild_id in self.history: self.history[guild_id] = []
            self.current_song[guild_id] = None
            voice_client.stop()
            await voice_client.disconnect()
            await ctx.send(embed=discord.Embed(description="⏹️ Fila limpa e bot desconectado.", color=discord.Color.dark_red()))

    @commands.command(name='skip')
    async def skip(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            await ctx.send(embed=discord.Embed(description="⏭️ Música pulada.", color=discord.Color.purple()))
            voice_client.stop()
        else:
            await ctx.send(embed=discord.Embed(description="Não há música tocando para pular.", color=discord.Color.orange()))

    @commands.command(name='back')
    async def back(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        guild_id = ctx.guild.id
        if guild_id in self.history and self.history[guild_id]:
            last_song = self.history[guild_id].pop()
            if guild_id in self.current_song and self.current_song[guild_id]:
                self.queues[guild_id].insert(0, self.current_song[guild_id])
            self.queues[guild_id].insert(0, last_song)
            await ctx.send(embed=discord.Embed(description="⏪ Voltando para a música anterior.", color=discord.Color.purple()))
            if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
                voice_client.stop()
            else:
                await self.play_next(ctx)
        else:
            await ctx.send(embed=discord.Embed(description="Não há músicas no histórico.", color=discord.Color.orange()))

    @commands.command(name='vol')
    async def vol(self, ctx: commands.Context, volume: int):
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_connected():
            if 0 <= volume <= 100:
                new_volume = volume / 100.0
                self.guild_volumes[ctx.guild.id] = new_volume
                if voice_client.source:
                    voice_client.source.volume = new_volume
                await ctx.send(embed=discord.Embed(description=f"🔊 Volume ajustado para **{volume}%**.", color=discord.Color.blue()))
            else:
                await ctx.send(embed=discord.Embed(description="O volume deve ser um número entre 0 e 100.", color=discord.Color.orange()))
                
    @commands.command(name='fila', aliases=['playlist', 'lista'])
    async def fila(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        embed = discord.Embed(title="🎵 Fila de Músicas", color=discord.Color.orange())
        if guild_id in self.current_song and self.current_song.get(guild_id):
            embed.add_field(name="Tocando Agora", value=f"**{self.current_song[guild_id]['title']}**", inline=False)
        if guild_id in self.queues and self.queues[guild_id]:
            queue_list = ""
            for i, song in enumerate(self.queues[guild_id][:10]):
                queue_list += f"**{i+1}.** {song['title']}\n"
            if len(self.queues[guild_id]) > 10:
                queue_list += f"\n... e mais {len(self.queues[guild_id]) - 10} música(s)."
            embed.add_field(name="Próximas na Fila", value=queue_list or "Nenhuma", inline=False)
        if not embed.fields: await ctx.send(embed=discord.Embed(description="A fila está vazia!", color=discord.Color.light_grey()))
        else: await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))