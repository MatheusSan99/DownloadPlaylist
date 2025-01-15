from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import os
from yt_dlp import YoutubeDL

class DownloaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.url_input = TextInput(hint_text='Digite a URL do vídeo ou playlist', multiline=False)
        self.layout.add_widget(self.url_input)
        
        self.download_button = Button(text='Baixar', on_press=self.download_media)
        self.layout.add_widget(self.download_button)
        
        self.status_label = Label(text='')
        self.layout.add_widget(self.status_label)
        
        return self.layout

    def download_media(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "URL inválida!"
            return

        options = {
            'format': 'best',
            'outtmpl': os.path.join('./downloads', '%(title)s.%(ext)s'),
        }
        os.makedirs('./downloads', exist_ok=True)
        try:
            with YoutubeDL(options) as ydl:
                ydl.download([url])
            self.status_label.text = "Download concluído!"
        except Exception as e:
            self.status_label.text = f"Erro: {e}"

if __name__ == '__main__':
    DownloaderApp().run()
