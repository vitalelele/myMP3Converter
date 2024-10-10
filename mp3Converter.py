import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QProgressBar, QLabel, QDialog, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap
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
        self.setWindowTitle("Settings / Impostazioni")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Selezione del tema
        self.theme_label = QLabel("Select Theme / Seleziona il tema:")
        layout.addWidget(self.theme_label)

        self.light_theme_radio = QRadioButton("Light / Chiaro")
        self.dark_theme_radio = QRadioButton("Dark / Scuro")
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

        # Selezione della lingua
        self.language_label = QLabel("Select Language / Seleziona la lingua:")
        layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Italiano"])
        layout.addWidget(self.language_combo)

        # Seleziona la lingua corrente
        current_language = self.parent().current_language
        self.language_combo.setCurrentText(current_language.capitalize())

        # Spazio vuoto
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Pulsante Salva
        self.save_button = QPushButton("Save / Salva")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        if self.light_theme_radio.isChecked():
            self.parent().apply_theme("light")
        else:
            self.parent().apply_theme("dark")

        # Ottieni il testo selezionato dalla combo box e convertilo in inglese
        selected_language = self.language_combo.currentText().lower()
        if selected_language == "inglese":
            selected_language = "english"
        elif selected_language == "italiano":
            selected_language = "italian"

        self.parent().apply_language(selected_language)
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Converter")
        self.setFixedSize(500, 300)

        # Tema corrente e lingua (di default "light" e "english")
        self.current_theme = "light"
        self.current_language = "english"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Convert / Converti")
        self.convert_button.clicked.connect(self.fetch_video_title)
        button_layout.addWidget(self.convert_button)

        self.open_folder_button = QPushButton("Open Folder / Apri Cartella")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        button_layout.addWidget(self.open_folder_button)

        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready for conversion / Pronto per la conversione")
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

        # Applica tema e lingua dopo che tutti i widget sono stati inizializzati
        self.apply_theme(self.current_theme)
        self.apply_language(self.current_language)

        self.setup_animations()

    def setup_animations(self):
        """Set up the animations for the progress bar."""
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(1000)  # 1 second
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutBounce)

    def apply_theme(self, theme):
        """Applica il tema selezionato."""
        self.current_theme = theme
        if theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0; 
                    color: #333333;
                }
                QPushButton {
                    background-color: #008CBA; 
                    color: white; 
                    border: none; 
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #005f75;
                }
                QProgressBar {
                    background-color: #e0e0e0;
                    border: 1px solid #008CBA;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212; 
                    color: white;
                }
                QPushButton {
                    background-color: #005f75; 
                    color: white; 
                    border: none; 
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #007f9b;
                }
                QProgressBar {
                    background-color: #333333;
                    border: 1px solid #005f75;
                }
            """)

    def apply_language(self, language):
        """Applica la lingua selezionata."""
        self.current_language = language
        translations = {
            "english": {
                "title": "YouTube to MP3 Converter",
                "placeholder": "Enter YouTube video URL",
                "status_ready": "Ready for conversion",
                "status_fetching": "Fetching video information...",
                "status_converting": "Converting...",
                "status_complete": "Conversion complete!",
                "status_error": "Error: {}",
                "confirm_conversion": "Do you want to convert the following video?\n\nTitle: {}",
                "button_convert": "Convert",
                "button_open_folder": "Open Folder",
                "settings": "Settings"
            },
            "italian": {
                "title": "Convertitore YouTube in MP3",
                "placeholder": "Inserisci l'URL del video YouTube",
                "status_ready": "Pronto per la conversione",
                "status_fetching": "Recupero informazioni video...",
                "status_converting": "Conversione in corso...",
                "status_complete": "Conversione completata!",
                "status_error": "Errore: {}",
                "confirm_conversion": "Vuoi convertire il seguente video?\n\nTitolo: {}",
                "button_convert": "Converti",
                "button_open_folder": "Apri Cartella",
                "settings": "Impostazioni"
            }
        }

        # Imposta le stringhe tradotte
        current_translations = translations[language]
        self.setWindowTitle(current_translations["title"])
        self.url_input.setPlaceholderText(current_translations["placeholder"])
        self.status_label.setText(current_translations["status_ready"])
        self.convert_button.setText(current_translations["button_convert"])
        self.open_folder_button.setText(current_translations["button_open_folder"])

    def fetch_video_title(self):
        """Recupera il titolo del video da YouTube."""
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText(self.get_translation("status_error").format("URL cannot be empty."))
            return

        self.status_label.setText(self.get_translation("status_fetching"))

        # Usa yt-dlp per recuperare il titolo
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "Unknown Title")
                self.confirm_conversion(title)
        except Exception as e:
            self.conversion_error(str(e))

    def confirm_conversion(self, title):
        """Mostra una finestra di conferma con il titolo del video prima della conversione."""
        translations = {
            "english": "Do you want to convert the following video?\n\nTitle: {}",
            "italian": "Vuoi convertire il seguente video?\n\nTitolo: {}"
        }
        confirm_message = translations[self.current_language].format(title)

        confirm = QMessageBox.question(self, self.tr("Confirm Conversion"), confirm_message,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            self.start_conversion()
        else:
            self.convert_button.setEnabled(True)
            self.status_label.setText("Conversion cancelled.")

    def start_conversion(self):
        """Inizia la conversione del video."""
        self.status_label.setText(self.get_translation("status_converting"))
        self.thread = DownloadThread(self.url_input.text(), self.download_folder, self.ffmpeg_path)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.error.connect(self.conversion_error)
        self.thread.start()

    def update_progress(self, value):
        """Aggiorna la barra di progresso."""
        self.progress_bar.setValue(value)

    def conversion_finished(self):
        translations = {
            "english": "Conversion complete!",
            "italian": "Conversione completata!"
        }
        self.status_label.setText(translations[self.current_language])
        self.convert_button.setEnabled(True)

    def conversion_error(self, error):
        translations = {
            "english": "Error: {}",
            "italian": "Errore: {}"
        }
        self.status_label.setText(translations[self.current_language].format(error))
        self.convert_button.setEnabled(True)

    def open_settings(self):
        """Apre il dialog delle impostazioni."""
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    def open_download_folder(self):
        """Apre la cartella di download."""
        os.startfile(self.download_folder)

    def get_translation(self, key):
        """Recupera la traduzione in base alla lingua corrente."""
        translations = {
            "english": {
                "status_ready": "Ready for conversion",
                "status_fetching": "Fetching video information...",
                "status_converting": "Converting...",
                "status_complete": "Conversion complete!",
                "status_error": "Error: {}"
            },
            "italian": {
                "status_ready": "Pronto per la conversione",
                "status_fetching": "Recupero informazioni video...",
                "status_converting": "Conversione in corso...",
                "status_complete": "Conversione completata!",
                "status_error": "Errore: {}"
            }
        }
        return translations[self.current_language][key]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
