# Gesahni

**Gesahni** is a simple project that converts audio to text using [OpenAI's Whisper](https://github.com/openai/whisper). It supports both command-line and browser-based recording, and it automatically organizes sessions by date.

---

## 🚀 Project Goals

- Convert audio to text using Whisper
- Automatically organize transcripts in daily folders
- Record audio/video via CLI or browser
- Serve as a base for future speech-to-text projects

---

## 🛠 Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/gesahni.git
cd gesahni

# 2. Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install ffmpeg (required by Whisper)
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
🧪 Running the Application
▶️ CLI Mode (Transcribe audio.wav)
# Place an audio.wav inside: sessions/YYYY-MM-DD/
python main.py
Output: transcript.txt in the same folder
Also prints the transcript to the console
🌐 Web Mode (Record Video/Audio in Browser)
# Start the server
python server.py
Open your browser: http://localhost:5000
Use the Start / Stop buttons to record
Click Send Audio to transcribe (requires Whisper installed)
📦 Dependencies
Python 3.8+
whisper (https://github.com/openai/whisper)
ffmpeg
Flask
🤝 Contributing
# 1. Fork this repo
# 2. Create a branch: git checkout -b feature-thing
# 3. Make your changes and commit
# 4. Open a pull request
Please write clean, documented code that follows Python best practices.
🧠 Future Ideas
Real-time mic transcription
Speaker detection
Upload multiple audio formats
Transcription previews in browser
Whisper model switching (tiny/base/large)
