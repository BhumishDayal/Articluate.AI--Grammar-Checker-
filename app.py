import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if 'score_history' not in st.session_state:
    st.session_state.score_history = []


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def estimate_duration(transcript):
    words = transcript.split()
    avg_wpm = 130 
    return len(words) / avg_wpm * 60  

def grammar_score(transcript, feedback_mode="default", temperature=0.0):
    mode_instruction = {
        "default": "",
        "teacher": "Give clear academic grammar feedback as a language teacher.",
        "business": "Tailor feedback for professional business communication.",
        "casual": "Give relaxed, friendly feedback like a language buddy."
    }.get(feedback_mode, "")

    prompt = (
        f"Evaluate the grammar quality of the following spoken text.\n"
        f"Also classify the type of content: is it a song, movie dialogue, podcast, conversation between friends, news report, or something else?\n"
        f"Comment on pronunciation clarity and speech fluency.\n"
        f"Return ONLY a JSON object with these keys: 'score', 'brief summary', 'specific suggestions', 'CEFR level', 'overall tone', 'type of content', 'pronunciation', 'corrections'.\n"
        f"{mode_instruction}\n"
        f"Do not include any explanation or introduction outside the JSON object.\n\n\"{transcript}\""
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )

    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Articulate.AI", page_icon="🎤", layout="centered")
st.title("🎙️ Articulate.AI")
st.markdown("Upload an audio file to get your grammar score, CEFR level, tone, pronunciation feedback, and content type analysis — powered by GPT-4.")

# Sidebar settings
with st.sidebar:
    st.header("    Made By - Bhumish Dayal    ")
    st.header("ℹ️ How to Use")
    st.markdown("""     
    1. Upload a `.wav` or `.mp3` file.
    2. Choose your feedback mode.
    3. See transcription + scoring + tips.
    4. Download or track your feedback.
    """)
    rescore = st.checkbox("🔁 Enable randomness for more creative feedback", value=False)
    feedback_mode = st.radio("🎭 Feedback Style", ["default", "teacher", "business", "casual"], index=0)

uploaded_files = st.file_uploader("📤 Upload one or more voice samples", type=["wav", "mp3"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.markdown(f"### 🔃 Processing: `{uploaded_file.name}`")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_audio_path = temp_file.name

        with st.spinner("🌀 Transcribing audio..."):
            transcript = transcribe_audio(temp_audio_path)
        st.success("✅ Transcription complete!")

        duration = estimate_duration(transcript)

        with st.expander("📝 View Transcribed Text"):
            st.write(transcript)

        temperature = 0.7 if rescore else 0.0

        with st.spinner("🤖 Analyzing with GPT..."):
            feedback = grammar_score(transcript, feedback_mode, temperature)
        st.success("✅ Feedback ready!")

        try:
            result = json.loads(feedback)
        except:
            st.error("⚠️ Could not parse GPT response. Showing raw feedback:")
            st.code(feedback)
            result = {
                "score": "?",
                "brief summary": "Could not extract summary.",
                "specific suggestions": "N/A",
                "CEFR level": "Unknown",
                "overall tone": "Unknown",
                "type of content": "Unclassified",
                "pronunciation": "Not evaluated",
                "corrections": []
            }

        st.subheader("📊 Feedback Summary")
        st.markdown(f"**Score:** {result.get('score', '?')}/10")
        st.markdown(f"**CEFR Level:** {result.get('CEFR level', 'Unknown')}")
        st.markdown(f"**Tone:** {result.get('overall tone', 'Unknown')}")
        st.markdown(f"**Content Type:** {result.get('type of content', 'Unclassified')}")
        st.markdown(f"**Pronunciation:** {result.get('pronunciation', 'Not evaluated')}")
        st.markdown(f"**Summary:** {result.get('brief summary', 'No summary provided.')}")
        st.markdown("**Suggestions:**")
        st.write(result.get("specific suggestions", "No suggestions provided."))

        corrections = result.get("corrections", [])
        if isinstance(corrections, str):
            corrections = [s.strip() for s in corrections.split('.') if s.strip()]
        if corrections:
            st.markdown("**🪄 Sample Corrections:**")
            for item in corrections:
                st.markdown(f"- {item}")

        words = transcript.split()
        wpm = len(words) / (duration / 60) if duration > 0 else 0
        st.metric("🗣️ Words per Minute", f"{wpm:.1f}")
        st.metric("📝 Word Count", len(words))

        score_for_history = result.get("score", 0)
        try:
            score_for_history = int(score_for_history)
        except:
            score_for_history = 0
        st.session_state.score_history.append((datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), score_for_history))

        full_text = f"""Transcript:\n{transcript}\n\nGrammar Score: {result.get('score', '?')}/10\nCEFR Level: {result.get('CEFR level', '?')}\nTone: {result.get('overall tone', '?')}\nContent Type: {result.get('type of content', 'Unclassified')}\nPronunciation: {result.get('pronunciation', '')}\nSummary: {result.get('brief summary', '')}\nSuggestions:\n{result.get('specific suggestions', '')}\nCorrections:\n{chr(10).join(corrections)}"""
        filename = f"GrammarFeedback_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        st.download_button("⬇️ Download Full Feedback", full_text, file_name=filename)

        st.audio(temp_audio_path, format='audio/wav')
        os.remove(temp_audio_path)
else:
    st.info("Upload one or more voice samples to begin.")

def score_to_emoji(score):
    if score >= 9:
        return "🌟"
    elif score >= 7:
        return "✅"
    elif score >= 5:
        return "⚠️"
    else:
        return "🚧"

if st.session_state.score_history:
    st.subheader("📅 Emoji Score Timeline")
    recent = st.session_state.score_history[-10:]
    for time, score in reversed(recent):
        st.markdown(f"{score_to_emoji(score)} `{time}` — **{score}/10**")

st.markdown("---")