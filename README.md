# 🎙️ Articulate.AI

An AI-powered grammar evaluation and feedback tool for spoken English. Upload `.wav` or `.mp3` audio files and receive a detailed grammar score, CEFR level, content classification, pronunciation feedback, and suggestions — all using OpenAI Whisper and GPT-4.

---

## 🚀 Features

- 🔊 Transcribe spoken English from audio
- ✍️ Analyze grammar, tone, and fluency
- 🧠 Uses GPT-4 for advanced language feedback
- 📊 Provides CEFR levels, WPM, and correction suggestions
- 🧾 Downloadable feedback report
- 🌐 Supports different feedback styles (teacher, business, casual)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/grammar-scorer.git
cd grammar-scorer
```

### 1. Set up virtual environment
```
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. API Key
```
Add your OPENAI_API_KEY in the .env file
```
 
### 4. Run the app
```
Streamlit run app.py
```