ChinaMusic - Bot de Música para Discord

🎵 Funcionalidades
Toca músicas de links do YouTube e Spotify.

Toca playlists do YouTube e Spotify.

Busca por nome de música (primeiro no Spotify, depois no YouTube).

Comandos de controle de player: play, pause, resume, skip, stop.

Comando para voltar para a música anterior (back).

Gerenciamento de fila (fila, lista, playlist).

Controle de volume (vol).

🛠️ Configuração e Instalação (Linux)
Siga estes passos para configurar o ambiente e rodar o bot em um sistema Linux.

1. Pré-requisitos
Python 3.11 ou superior (versão estável recomendada).

FFmpeg instalado e acessível no PATH do sistema.

Git.

2. Passos de Instalação
Clone o repositório:

Bash

git clone https://github.com/ChinaLofy/ChinaMusic-2.0.git
cd ChinaMusic
Crie e ative o ambiente virtual:

Bash

python3 -m venv venv
source venv/bin/activate
Instale as dependências do Python:

Bash

pip install -r requirements.txt
Configure as variáveis de ambiente:

Crie um arquivo chamado .env na raiz do projeto.

Adicione suas chaves e tokens neste arquivo, seguindo o modelo abaixo:

Snippet de código

DISCORD_TOKEN=SEU_TOKEN_DO_DISCORD_AQUI
SPOTIPY_CLIENT_ID=SEU_CLIENT_ID_DO_SPOTIFY_AQUI
SPOTIPY_CLIENT_SECRET=SEU_CLIENT_SECRET_DO_SPOTIFY_AQUI
🚀 Como Rodar o Bot
Com o ambiente virtual ativado ((venv)) e o arquivo .env configurado, inicie o bot com o comando:

python3 startbot.py

# ChinaMusic-2.0
Bot de Musica para Discord
