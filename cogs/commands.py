import discord
from discord.ext import commands
from discord import app_commands

class GeneralCog(commands.Cog, name="Geral"):
    """Cog para comandos gerais e de utilidade do bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog Geral carregado.")

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Mostra a mensagem de ajuda com todos os comandos."""
        embed = discord.Embed(
            title="🎶 Comandos do Bot",
            description=f"Prefixo atual: `{self.bot.command_prefix}`",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="`play <link/nome>` ou `p <link/nome>`", value="Toca uma música ou playlist do YouTube/Spotify.", inline=False)
        embed.add_field(name="`pause`", value="Pausa a música atual.", inline=False)
        embed.add_field(name="`resume`", value="Continua a música pausada.", inline=False)
        embed.add_field(name="`stop`", value="Para a música, limpa a fila e desconecta o bot.", inline=False)
        embed.add_field(name="`skip`", value="Pula para a próxima música da fila.", inline=False)
        embed.add_field(name="`back`", value="Volta para a música anterior.", inline=False)
        embed.add_field(name="`fila` ou `lista` ou `playlist`", value="Mostra a fila de músicas.", inline=False)
        embed.add_field(name="`vol <0-100>`", value="Ajusta o volume (ex: `c!vol 50`).", inline=False)
        embed.set_footer(text=f"Bot requisitado por: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        """Mede a latência do bot com a API do Discord."""
        latency = self.bot.latency * 1000  # Converte para milissegundos
        await ctx.send(f'Pong! 🏓 Latência da API: **{latency:.2f}ms**')
    
    @app_commands.command(name="china", description="Envia informações sobre o desenvolvedor.")
    async def china_slash(self, interaction: discord.Interaction):
        """Comando de barra que envia uma mensagem personalizada."""
        china_art = "Bot Developed By China #LOFY (Discord: ooriente)"
        await interaction.response.send_message(f"```\n{china_art}\n```")


async def setup(bot: commands.Bot):
    """Função chamada pelo discord.py para carregar a Cog."""
    await bot.add_cog(GeneralCog(bot))