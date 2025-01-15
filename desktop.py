import os
import threading
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, messagebox, Radiobutton
from tkinter.ttk import Progressbar
from yt_dlp import YoutubeDL
import re

parar_download = False
baixados = []
nao_baixados = []
todos_os_videos = []

def exibir_mensagem(tipo, titulo, mensagem):
    if tipo == "info":
        messagebox.showinfo(titulo, mensagem)
    elif tipo == "warning":
        messagebox.showwarning(titulo, mensagem)
    elif tipo == "error":
        messagebox.showerror(titulo, mensagem)

def hook_progresso(d):
    global parar_download

    if parar_download:
        raise Exception("Download interrompido pelo usuário.")

    if d['status'] == 'downloading':
        percentual_str = d.get('_percent_str', '0.0%').strip()
        match = re.search(r'(\d+(\.\d+)?)(?=%)', percentual_str)

        if match:
            percentual_str = match.group(0)
            try:
                percentual = float(percentual_str)
                progresso_individual["value"] = percentual
                janela.update_idletasks()
            except ValueError:
                progresso_individual["value"] = 0
        else:
            progresso_individual["value"] = 0
    elif d['status'] == 'finished':
        progresso_individual["value"] = 100

def baixar_midia(url, pasta_destino, formato, playlist):
    global baixados, nao_baixados, parar_download, todos_os_videos
    opcoes = {
        'outtmpl': os.path.join(pasta_destino, '%(playlist_title)s/%(title)s.%(ext)s'),
        'noplaylist': not playlist,
        'nocheckcertificate': True,
        'progress_hooks': [hook_progresso],
    }

    if formato == 'audio':
        opcoes.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    elif formato == 'video':
        opcoes.update({'format': 'bestvideo+bestaudio'})

    try:
        with YoutubeDL(opcoes) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [info]) if 'entries' in info else [info]
            except Exception as e:
                print(f"Erro ao obter informações da playlist: {e}")
                exibir_mensagem("error", "Erro", f"Erro ao obter informações da playlist: {e}")
                return

            total_videos = len(entries)

            for entry in entries:
                nao_baixados.append({'title': entry.get('title', 'Sem título'), 'webpage_url': entry.get('webpage_url', '')})
                todos_os_videos.append({'title': entry.get('title', 'Sem título'), 'webpage_url': entry.get('webpage_url', '')})

            for index, entry in enumerate(entries, start=1):
                if parar_download:
                    break

                try:
                    progresso_playlist["value"] = (index / total_videos) * 100
                    janela.update_idletasks()

                    ydl.download([entry['webpage_url']])

                    baixados.append(entry['title'])
                    nao_baixados = [
                        video for video in nao_baixados 
                        if video['title'] != entry['title']
                    ]

                except Exception as e:
                    print(f"Erro ao baixar {entry.get('title', 'Sem título')}: {e}")
                    continue 

        if parar_download:
            exibir_mensagem("info", "Interrompido", "O download foi interrompido pelo usuário.")
        else:
            exibir_mensagem("info", "Sucesso", "Download concluído!")

    except Exception as e:
        exibir_mensagem("error", "Erro", f"Erro ao processar a playlist: {e}")

    progresso_individual["value"] = 0
    progresso_playlist["value"] = 0
    botao_download.config(state="normal")

    gerar_relatorio(pasta_destino)

def gerar_relatorio(pasta_destino):
    global baixados, nao_baixados

    relatorio_path = os.path.join(pasta_destino, "relatorio_download.txt")
    videos_baixados_atuais = set(baixados)
    videos_nao_baixados_atuais = set(
        (video['title'], video['webpage_url']) for video in nao_baixados
    )

    try:
        if os.path.exists(relatorio_path):
            with open(relatorio_path, "r", encoding="utf-8") as relatorio:
                linhas = relatorio.readlines()

            lendo_nao_baixados = False
            lendo_baixados = False
            for linha in linhas:
                linha = linha.strip()
                if "Vídeos Baixados" in linha:
                    lendo_baixados = True
                    lendo_nao_baixados = False
                    continue
                if "Vídeos Não Baixados" in linha:
                    lendo_nao_baixados = True
                    lendo_baixados = False
                    continue
                if lendo_baixados and linha != "":
                    videos_baixados_atuais.add(linha)
                if lendo_nao_baixados and " | " in linha:
                    title, url = linha.split(" | ", 1)
                    videos_nao_baixados_atuais.add((title, url))
    except Exception as e:
        print(f"Erro ao carregar relatório existente: {e}")

    videos_nao_baixados_atuais = {
        (title, url) for title, url in videos_nao_baixados_atuais
        if title not in videos_baixados_atuais
    }

    try:
        with open(relatorio_path, "w", encoding="utf-8") as relatorio:
            relatorio.write("Vídeos Baixados:\n")
            relatorio.write("\n".join(sorted(videos_baixados_atuais)) + "\n\n")
            relatorio.write("Vídeos Não Baixados (Título | Link):\n")
            for title, url in sorted(videos_nao_baixados_atuais):
                relatorio.write(f"{title} | {url}\n")
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")

    print(f"Relatório atualizado em: {relatorio_path}")

def selecionar_pasta():
    pasta = filedialog.askdirectory()
    pasta_var.set(pasta)

def validacoes_iniciais(url, pasta_destino, relatorio=False, caminho_relatorio=None):
    if not relatorio:
        if not url.startswith("http"):
            exibir_mensagem("warning", "URL inválida", "A URL informada é inválida!")
            return False

    if not pasta_destino:
        exibir_mensagem("warning", "Campos obrigatórios", "É obrigatório preencher a pasta de destino!")
        return False

    if relatorio:
        if not caminho_relatorio:  
            exibir_mensagem("warning", "Arquivo inválido", "Selecione um arquivo de relatório!")
            return False

    return True

def iniciar_download():
    global parar_download, baixados, nao_baixados

    url = url_var.get().strip()
    formato = formato_var.get()
    playlist = playlist_var.get() == "Sim"
    pasta_destino = pasta_var.get()

    if not validacoes_iniciais(url, pasta_destino):
        return

    progresso_individual["value"] = 0
    progresso_playlist["value"] = 0
    baixados = []
    nao_baixados = []

    botao_download.config(state="disabled")

    threading.Thread(target=baixar_midia, args=(url, pasta_destino, formato, playlist), daemon=True).start()

def parar_execucao():
    global parar_download
    parar_download = True

def carregar_e_processar_relatorio():
    global parar_download

    formato = formato_var.get()
    playlist = playlist_var.get() == "Sim"
    pasta_destino = pasta_var.get()
    caminho_relatorio = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])

    if not validacoes_iniciais('', pasta_destino, True, caminho_relatorio):
        return

    threading.Thread(target=processar_relatorio, args=(caminho_relatorio, pasta_destino, formato, playlist), daemon=True).start()

def processar_relatorio(caminho_relatorio, pasta_destino, formato, playlist):
    global parar_download

    baixados = []
    nao_baixados = []

    try:
        if os.path.exists(caminho_relatorio):
            with open(caminho_relatorio, "r", encoding="utf-8") as relatorio:
                linhas = relatorio.readlines()

            lendo_nao_baixados = False
            for linha in linhas:
                linha = linha.strip()
                if "Vídeos Baixados" in linha:
                    lendo_nao_baixados = False
                elif "Vídeos Não Baixados" in linha:
                    lendo_nao_baixados = True
                    continue
                elif lendo_nao_baixados and " | " in linha:
                    title, url = linha.split(" | ", 1)
                    nao_baixados.append({'title': title, 'webpage_url': url})
                elif not lendo_nao_baixados and linha:
                    baixados.append(linha)

        total_videos = len(nao_baixados)
        if not total_videos:
            messagebox.showinfo("Nenhum Item", "Todos os vídeos já foram baixados!")
            return

        for index, item in enumerate(nao_baixados.copy(), start=1):
            if parar_download:
                break

            try:
                progresso_percentual = (index / total_videos) * 100
                atualizar_progresso(progresso_playlist, progresso_percentual)
                baixar_midia(item['webpage_url'], pasta_destino, formato, playlist)
                baixados.append(item['title'])
                nao_baixados.remove(item)

            except Exception as e:
                print(f"Erro ao baixar {item['title']}: {e}")
                pass

        mensagem = "Download foi interrompido pelo usuário." if parar_download else "Reprocessamento concluído!"
        messagebox.showinfo("Status", mensagem)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar relatório: {e}")

    atualizar_progresso(progresso_individual, 0)
    atualizar_progresso(progresso_playlist, 0)
    botao_download.config(state="normal")
    gerar_relatorio(pasta_destino)

def atualizar_progresso(progresso_barra, percentual):
    try:
        progresso_barra["value"] = percentual
        janela.update_idletasks()
    except ValueError:
        progresso_barra["value"] = 0

janela = Tk()
janela.title("Downloader de Mídia")
janela.geometry("800x550")
janela.configure(bg="#f5f5f5")

url_var = StringVar()
formato_var = StringVar(value="audio")
playlist_var = StringVar(value="Não")
pasta_var = StringVar()

# Linha 1: URL
Label(janela, text="URL do vídeo ou playlist:", bg="#f5f5f5").grid(row=0, column=0, padx=10, pady=10, sticky="w")
Entry(janela, textvariable=url_var, width=50).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

# Linha 2: Formato
Label(janela, text="Formato:", bg="#f5f5f5").grid(row=2, column=0, padx=10, pady=10, sticky="w")
Radiobutton(janela, text="Áudio (MP3)", variable=formato_var, value="audio", bg="#f5f5f5").grid(row=3, column=0, padx=10, pady=5, sticky="w")
Radiobutton(janela, text="Vídeo", variable=formato_var, value="video", bg="#f5f5f5").grid(row=4, column=0, padx=10, pady=5, sticky="w")

# Linha 3: Playlist
Label(janela, text="É uma playlist?", bg="#f5f5f5").grid(row=5, column=0, padx=10, pady=10, sticky="w")
Radiobutton(janela, text="Sim", variable=playlist_var, value="Sim", bg="#f5f5f5").grid(row=6, column=0, padx=10, pady=5, sticky="w")
Radiobutton(janela, text="Não", variable=playlist_var, value="Não", bg="#f5f5f5").grid(row=7, column=0, padx=10, pady=5, sticky="w")

# Linha 4: Pasta de destino
Label(janela, text="Pasta de destino:", bg="#f5f5f5").grid(row=8, column=0, padx=10, pady=10, sticky="w")
Entry(janela, textvariable=pasta_var, width=40).grid(row=8, column=1, padx=10, pady=10, sticky="ew")
Button(janela, text="Selecionar Pasta", command=selecionar_pasta).grid(row=8, column=2, padx=10, pady=10, sticky="w")

# Linha 5: Reprocessar Relatório
Label(janela, text="Reprocessar Relatório:", bg="#f5f5f5").grid(row=9, column=0, padx=10, pady=10, sticky="w")
Entry(janela, width=40).grid(row=9, column=1, padx=10, pady=10, sticky="ew")
Button(janela, text="Reprocessar Relatório", command=carregar_e_processar_relatorio, bg="blue", fg="white").grid(row=9, column=2, padx=10, pady=10, sticky="w")

# Linha 6: Barras de Progresso
Label(janela, text="Progresso do Download:", bg="#f5f5f5").grid(row=10, column=0, padx=10, pady=10, sticky="w")
progresso_individual = Progressbar(janela, orient="horizontal", length=300, mode="determinate")
progresso_individual.grid(row=10, column=1, padx=10, pady=10, sticky="ew")

Label(janela, text="Progresso da Playlist:", bg="#f5f5f5").grid(row=11, column=0, padx=10, pady=10, sticky="w")
progresso_playlist = Progressbar(janela, orient="horizontal", length=300, mode="determinate")
progresso_playlist.grid(row=11, column=1, padx=10, pady=10, sticky="ew")

# Linha 7: Botões Iniciar e Parar Download
botao_download = Button(janela, text="Iniciar Download", command=iniciar_download, bg="green", fg="white")
botao_download.grid(row=12, column=0, columnspan=3, pady=15, padx=10, sticky="ew")
Button(janela, text="Parar Download", command=parar_execucao, bg="red", fg="white").grid(row=13, column=0, columnspan=3, pady=15, padx=10, sticky="ew")

janela.grid_columnconfigure(0, weight=1)
janela.grid_columnconfigure(1, weight=2)
janela.grid_columnconfigure(2, weight=1)
janela.grid_rowconfigure(0, weight=1)
janela.grid_rowconfigure(1, weight=1)
janela.grid_rowconfigure(2, weight=1)
janela.grid_rowconfigure(3, weight=1)
janela.grid_rowconfigure(4, weight=1)
janela.grid_rowconfigure(5, weight=1)
janela.grid_rowconfigure(6, weight=1)
janela.grid_rowconfigure(7, weight=1)
janela.grid_rowconfigure(8, weight=1)
janela.grid_rowconfigure(9, weight=1)
janela.grid_rowconfigure(10, weight=1)
janela.grid_rowconfigure(11, weight=1)
janela.grid_rowconfigure(12, weight=1)
janela.grid_rowconfigure(13, weight=1)

janela.mainloop()
