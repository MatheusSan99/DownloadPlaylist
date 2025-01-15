# Media Downloader

Este projeto é uma aplicação em Python que permite realizar o download de vídeos ou áudios de URLs, com suporte para geração e reprocessamento de relatórios. A interface gráfica foi desenvolvida utilizando tkinter, e o gerenciamento de downloads é feito com yt_dlp.

## Funcionalidades

- **Download de vídeos ou áudios**: Suporta download no formato MP3 ou de vídeo completo.
- **Geração de relatórios**: Relatório detalhado de downloads bem-sucedidos e falhas.
- **Reprocessamento de downloads**: Permite reexecutar downloads pendentes a partir de um relatório.
- **Progresso visual**: Barras de progresso para download individual e progresso geral da playlist.
- **Interrupção de downloads**: Possibilidade de pausar o processo a qualquer momento.

### Instalação e Uso com Docker

#### Pré-requisitos
Antes de continuar, certifique-se de que possui o Docker instalado em sua máquina:
- **Docker** (versão 20.10 ou superior)

Caso ainda não tenha o Docker instalado:
- **Ubuntu/Debian:**
  ```bash
  sudo apt update
  sudo apt install docker.io
  ```
- **Windows/Mac:** 
  Baixe e instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### Passos para Instalação com Docker

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/MatheusSan99/MediaDownloader.git
   cd MediaDownloader
   ```

2. **Construa a imagem Docker:**
   Execute o comando abaixo para criar a imagem Docker com base no `Dockerfile`:
   ```bash
   docker build -t media-downloader .
   ```

3. **Execute o container:**
   Após a construção da imagem, execute o container:
   ```bash
   docker run -it --rm -v "$(pwd)/downloads:/app/downloads" media-downloader
   ```
   - O comando acima monta a pasta local `downloads` como volume no container, permitindo que os arquivos baixados fiquem acessíveis fora do container.

4. **Interaja com o aplicativo:**
   O script principal será executado dentro do container. Basta seguir as instruções na interface gráfica ou no terminal conforme o uso padrão.

#### Parâmetros opcionais
Se necessário, você pode personalizar o comando de execução do Docker:
- Para especificar uma pasta de destino diferente:
  ```bash
  docker run -it --rm -v "/caminho/para/minha/pasta:/app/downloads" media-downloader
  ```

#### Atualizando a imagem
Caso realize alterações no código ou adicione dependências, reconstrua a imagem:
```bash
docker build -t media-downloader .
```
### Configuração inicial:

1. Insira a URL do vídeo ou playlist no campo apropriado.
2. Escolha o formato (áudio ou vídeo).
3. Especifique se o conteúdo é uma playlist.
4. Selecione a pasta de destino onde os arquivos serão salvos.

### Iniciar o download:

Clique em "Iniciar Download" para começar.

Utilize a barra de progresso para acompanhar o progresso individual e geral.

### Interromper downloads:

Clique em "Parar Download" para cancelar o processo a qualquer momento.

### Reprocessar relatório:

Selecione um arquivo de relatório existente e clique em "Reprocessar Relatório" para baixar os itens que falharam anteriormente.

## Arquivo de Relatório

O relatório gerado está localizado na pasta de destino selecionada e contém:

- **Vídeos Baixados**: Lista dos títulos baixados com sucesso.
- **Vídeos Não Baixados**: Lista de títulos e URLs que não foram baixados.

## Estrutura do Projeto

- **hook_progresso**: Atualiza a barra de progresso durante o download.
- **baixar_midia**: Gerencia o processo de download e configura o yt_dlp.
- **gerar_relatorio**: Cria ou atualiza o relatório de download.
- **processar_relatorio**: Permite reprocessar os downloads pendentes a partir de um relatório.
- **Interface gráfica**: Gerencia os campos de entrada e botões para facilitar o uso do aplicativo.