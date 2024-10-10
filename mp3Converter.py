import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QProgressBar, QLabel
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
import yt_dlp


class DownloadThread(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, download_folder, ffmpeg_path):
        super().__init__()
        self.url = url
        self.download_folder = download_folder
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'ffmpeg_location': self.ffmpeg_path,
            'progress_hooks': [self.progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                else:
                    progress = 0
                self.progress.emit(progress)
            except Exception as e:
                print(f"Errore nel calcolo del progresso: {e}")
                # In caso di errore, non emettiamo alcun segnale di progresso


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Converter")
        self.setFixedSize(500, 250)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #3498DB;
                border-radius: 3px;
                background-color: #34495E;
                color: #ECF0F1;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QProgressBar {
                border: 2px solid #3498DB;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2ECC71;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Inserisci l'URL del video YouTube")
        layout.addWidget(self.url_input)

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converti")
        self.convert_button.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.convert_button)

        self.open_folder_button = QPushButton("Apri Cartella")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        button_layout.addWidget(self.open_folder_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pronto per la conversione")
        layout.addWidget(self.status_label)

        self.download_folder = "download_mp3"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        self.ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'  # Modifica questo percorso se necessario

    def start_conversion(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Per favore, inserisci un URL valido")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Conversione in corso...")

        self.thread = DownloadThread(url, self.download_folder, self.ffmpeg_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.error.connect(self.conversion_error)
        self.thread.start()

    def update_progress(self, progress):
        self.progress_bar.setValue(int(progress))

    def conversion_finished(self):
        self.status_label.setText("Conversione completata!")
        self.convert_button.setEnabled(True)

    def conversion_error(self, error):
        self.status_label.setText(f"Errore: {error}")
        self.convert_button.setEnabled(True)

    def open_download_folder(self):
        os.startfile(self.download_folder)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())