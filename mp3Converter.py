import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QProgressBar, QLabel, QDialog, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap, QColor
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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Impostazioni")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Selezione del tema
        self.theme_label = QLabel("Seleziona il tema:")
        layout.addWidget(self.theme_label)

        self.light_theme_radio = QRadioButton("Chiaro")
        self.dark_theme_radio = QRadioButton("Scuro")
        layout.addWidget(self.light_theme_radio)
        layout.addWidget(self.dark_theme_radio)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.light_theme_radio)
        self.button_group.addButton(self.dark_theme_radio)

        # Seleziona il tema corrente
        current_theme = self.parent().current_theme
        if current_theme == "light":
            self.light_theme_radio.setChecked(True)
        else:
            self.dark_theme_radio.setChecked(True)

        # Spazio vuoto
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Pulsante Salva
        self.save_button = QPushButton("Salva")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        if self.light_theme_radio.isChecked():
            self.parent().apply_theme("light")
        else:
            self.parent().apply_theme("dark")
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Converter")
        self.setFixedSize(500, 300)

        # Tema corrente (di default "light")
        self.current_theme = "light"
        self.apply_theme(self.current_theme)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Inserisci l'URL del video YouTube")
        layout.addWidget(self.url_input)

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converti")
        self.convert_button.clicked.connect(self.fetch_video_title)
        button_layout.addWidget(self.convert_button)

        self.open_folder_button = QPushButton("Apri Cartella")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        button_layout.addWidget(self.open_folder_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pronto per la conversione")
        layout.addWidget(self.status_label)

        # Cartella download e path FFMPEG
        self.download_folder = "download_mp3"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

        self.ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'  # Modifica questo percorso se necessario

        # Aggiungi icona impostazioni in basso a destra
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(QPixmap('settings_icon.png')))
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.setIconSize(self.settings_button.size())
        self.settings_button.setStyleSheet("background-color: transparent; border: none;")
        self.settings_button.clicked.connect(self.open_settings)

        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setup_animations()

    def setup_animations(self):
        """Set up the animations for the progress bar."""
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(1000)  # 1 second
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutBounce)

    def fetch_video_title(self):
        """Fetch video title before starting conversion."""
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Per favore, inserisci un URL valido")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Recupero informazioni video...")

        # Creiamo un thread temporaneo per recuperare il titolo
        self.thread_title = DownloadThread(url, self.download_folder, self.ffmpeg_path)
        self.thread_title.finished.connect(self.get_video_title)
        self.thread_title.error.connect(self.conversion_error)
        self.thread_title.start()

    def get_video_title(self):
        """Get the video title after fetching info."""
        url = self.url_input.text()
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                self.confirm_conversion(title)
        except Exception as e:
            self.conversion_error(str(e))

    def confirm_conversion(self, title):
        """Show a confirmation dialog with the video title before conversion."""
        confirm = QMessageBox.question(self, "Conferma Conversione",
                                       f"Vuoi convertire il seguente video?\n\nTitolo: {title}",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            self.start_conversion()
        else:
            self.convert_button.setEnabled(True)
            self.status_label.setText("Conversione annullata.")

    def start_conversion(self):
        """Start the actual conversion after confirmation."""
        url = self.url_input.text()

        self.status_label.setText("Conversione in corso...")

        self.thread = DownloadThread(url, self.download_folder, self.ffmpeg_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.error.connect(self.conversion_error)
        self.thread.start()

    def update_progress(self, progress):
        self.progress_animation.stop()
        self.progress_animation.setStartValue(self.progress_bar.value())
        self.progress_animation.setEndValue(int(progress))
        self.progress_animation.start()

    def conversion_finished(self):
        self.status_label.setText("Conversione completata!")
        self.convert_button.setEnabled(True)

    def conversion_error(self, error):
        self.status_label.setText(f"Errore: {error}")
        self.convert_button.setEnabled(True)

    def open_download_folder(self):
        os.startfile(self.download_folder)

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_theme(self, theme):
        """Applica il tema selezionato."""
        if theme == "light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #E8F6F3;
                }
                QLabel {
                    color: #2E4053;
                    font-size: 14px;
                }
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #1ABC9C;
                    border-radius: 15px;
                    background-color: #FFFFFF;
                    color: #2E4053;
                }
                QPushButton {
                    padding: 10px 20px;
                    background-color: #1ABC9C;
                    color: white;
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16A085;
                }
                QProgressBar {
                    border: 2px solid #1ABC9C;
                    border-radius: 10px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #2ECC71;
                    border-radius: 10px;
                }
                QPushButton#settings_button {
                    background-color: #1ABC9C;
                    border-radius: 50%;
                }
                QPushButton#settings_button:hover {
                    background-color: #16A085;
                }
            """)
        else:
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
                    border-radius: 15px;
                    background-color: #34495E;
                    color: #ECF0F1;
                }
                QPushButton {
                    padding: 10px 20px;
                    background-color: #1ABC9C;  # Colore principale
                    color: white;
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #16A085;
                }
                QProgressBar {
                    border: 2px solid #3498DB;
                    border-radius: 10px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #E74C3C;  # Colore del chunk della progress bar
                    border-radius: 10px;
                }
                QPushButton#settings_button {
                    background-color: #E74C3C;  # Colore del pulsante impostazioni
                    border-radius: 50%;
                }
                QPushButton#settings_button:hover {
                    background-color: #C0392B;
                }
            """)
        self.current_theme = theme


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
