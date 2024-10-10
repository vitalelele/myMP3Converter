# myMP3Converter 🎵

myMP3Converter is a simple and intuitive desktop application that allows users to convert YouTube videos to MP3 format. Built using PyQt6 and yt-dlp, this tool offers a clean interface and customizable settings for a seamless experience.

## Features 🌟

- 🎶 Convert YouTube videos to MP3 audio format.
- 📊 Progress bar to track download progress.
- 📂 Ability to open the download folder directly from the app.
- 🎨 Customizable light and dark themes.
- 👤 User-friendly interface for inputting video URLs.

## Requirements 📋

- 🐍 Python 3.x
- 🖥️ PyQt6
- 🎥 yt-dlp
- ⚙️ FFmpeg (ensure the path is correctly set)

## Installation ⚙️

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vitalelele/myMP3Converter.git
   cd myMP3Converter
   ```

2. **Install the required Python packages:**
   ```bash
   pip install PyQt6 yt-dlp
   ```

3. **Install FFmpeg:**
   - Download FFmpeg from the [official site](https://ffmpeg.org/download.html).
   - Select your operating system and download the appropriate package.
   - Extract the downloaded files to a folder (e.g., `C:\ffmpeg`).
   - Add the FFmpeg `bin` directory to your system's PATH:
     - **Windows:**
       - Right-click on "This PC" or "My Computer" and select "Properties."
       - Click on "Advanced system settings," then "Environment Variables."
       - In the "System variables" section, find and select the `Path` variable, then click "Edit."
       - Click "New" and add the path to the `bin` folder (e.g., `C:\ffmpeg\bin`).
       - Click "OK" to close all dialogs.
     - **macOS/Linux:**
       - Open a terminal and run:
         ```bash
         echo 'export PATH="$PATH:/path/to/ffmpeg/bin"' >> ~/.bash_profile
         source ~/.bash_profile
         ```

## Usage 📖

1. **Run the application:**
   ```bash
   python main.py
   ```

2. In the application window, input the YouTube video URL in the provided text field.

3. Click the "Convert" button. The application will fetch the video title and prompt for confirmation before proceeding with the download.

4. During the conversion, the progress bar will update to show the current download status.

5. Once the conversion is complete, a message will notify you, and you can click "Open Folder" to access your downloaded MP3 file.

6. To change the theme, click on the settings icon, select your preferred theme, and save the changes.

## Contributing 🤝

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License 📄

This project is licensed under the MIT License. See the LICENSE file for details.
