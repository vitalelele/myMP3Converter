import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QProgressBar, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor
import yt_dlp

class DownloadThread(QThread):
    """Thread per gestire il download senza bloccare l'interfaccia."""
    progress = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, download_folder, ffmpeg_path):
        super().__init__()
        self.url = url
        self.download_folder = download_folder
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        """Avvia il download e conversione dell'MP3."""
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
        """Gestisce il progresso del download."""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            progress = (downloaded / total) * 100 if total > 0 else 0
            self.progress.emit(progress)


class MainWindow(QMainWindow):
    """Interfaccia grafica principale."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Converter 🎵")
        self.setFixedSize(550, 350)
        self.setStyleSheet("background-color: #181818; color: white; font-family: Arial;")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # **TITOLO**
        title_label = QLabel("🎵 YouTube MP3 Converter")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00A8E8;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # **BARRA URL + PULSANTI**
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL...")
        self.url_input.setStyleSheet("""
            background: #303030;
            border: 2px solid #00A8E8;
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-size: 14px;
        """)
        input_layout.addWidget(self.url_input)

        self.convert_button = QPushButton("🎧 Convert")
        self.convert_button.setStyleSheet(self.get_button_style())
        self.convert_button.clicked.connect(self.start_conversion)
        input_layout.addWidget(self.convert_button)

        main_layout.addLayout(input_layout)

        # **PROGRESS BAR**
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00A8E8;
                border-radius: 10px;
                background-color: #282828;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00A8E8, stop:1 #008CBA);
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # **STATUS LABEL**
        self.status_label = QLabel("🔵 Ready to convert...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        main_layout.addWidget(self.status_label)

        # **SEPARATORE**
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #555555;")
        main_layout.addWidget(separator)

        # **PULSANTE APRI CARTELLA**
        self.open_folder_button = QPushButton("📁 Open Folder")
        self.open_folder_button.setStyleSheet(self.get_button_style())
        self.open_folder_button.clicked.connect(self.open_download_folder)
        main_layout.addWidget(self.open_folder_button)

        # **OMBREGGIATURA**
        self.add_shadow_effect(self.url_input)
        self.add_shadow_effect(self.convert_button)
        self.add_shadow_effect(self.progress_bar)
        self.add_shadow_effect(self.open_folder_button)

        # **SETUP ANIMAZIONE**
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(500)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.download_folder = "download_mp3"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def get_button_style(self):
        """Stile dei pulsanti."""
        return """
            QPushButton {
                background: #008CBA;
                border: none;
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00A8E8;
            }
        """

    def add_shadow_effect(self, widget):
        """Aggiunge un'ombra per un effetto visivo migliore."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(3, 3)
        shadow.setColor(QColor(0, 168, 232, 100))  # Ombra azzurra traslucida
        widget.setGraphicsEffect(shadow)

    def start_conversion(self):
        """Avvia la conversione del video."""
        self.status_label.setText("⏳ Converting...")
        self.progress_bar.setValue(0)
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("❌ Error: URL cannot be empty!")
            return

        self.thread = DownloadThread(url, self.download_folder, r"C:\ffmpeg-2025-02-24-git-6232f416b1-full_build\bin\ffmpeg.exe")
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.error.connect(self.conversion_error)
        self.thread.start()

    def update_progress(self, value):
        """Aggiorna la progress bar con un'animazione fluida."""
        self.progress_animation.setStartValue(self.progress_bar.value())
        self.progress_animation.setEndValue(int(value))
        self.progress_animation.start()

    def conversion_finished(self):
        self.status_label.setText("✅ Conversion complete!")

    def conversion_error(self, error):
        self.status_label.setText(f"❌ Error: {error}")

    def open_download_folder(self):
        """Apre la cartella di download."""
        os.startfile(self.download_folder)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
