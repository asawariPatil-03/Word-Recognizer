import streamlit as st
import os
from speech_engine import SpeechEngine
from dictionary_api import DictionaryAPI
import requests

@st.cache_data
def get_pronunciation_audio(word: str) -> bytes:
    """Fetches pronunciation MP3 bytes from Google Translate TTS API."""
    if not word or not word.strip():
        return b""
    clean_word = word.strip().lower()
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={clean_word}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return b""

# Configure Page
st.set_page_config(
    page_title="Alle - Word Recognizer & Coach",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load and Inject CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

load_css()

# Initialize Helpers
speech_engine = SpeechEngine()

# Initialize Session State
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = []
if 'last_transcribed' not in st.session_state:
    st.session_state.last_transcribed = None
if 'custom_word' not in st.session_state:
    st.session_state.custom_word = ""

# App Title Header
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px;">
        <h1 class="gradient-text" style="font-size: 2.8rem; margin-bottom: 5px;">🎙️ Alle</h1>
        <p style="color: #94a3b8; font-size: 1.1rem; font-weight: 500;">
            Premium Voice Word Recognizer & Pronunciation Coach
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style="padding: 10px 0px;">
        <h2 style="font-size: 1.4rem; margin-bottom: 5px; color: #ffffff;">Navigation</h2>
        <hr style="border: 0; height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 20px;" />
    </div>
    """,
    unsafe_allow_html=True
)

mode = st.sidebar.radio(
    "Choose Application Mode",
    [
        "🎙️ Word Transcriber",
        "🏆 Pronunciation Coach",
        "📖 Word Explorer"
    ]
)

st.sidebar.markdown("<br><hr style='border:0; height:1px; background:rgba(255,255,255,0.1);'/><br>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div class="glass-card" style="padding: 15px; font-size: 0.9rem;">
        <h4 style="margin-top:0; color:#818cf8;">How it works:</h4>
        <ul style="padding-left: 20px; color:#cbd5e1; margin-bottom:0;">
            <li>Records audio in browser.</li>
            <li>Transcribes using Google Web Speech.</li>
            <li>Analyzes differences using SequenceMatcher.</li>
            <li>Fetches definitions from DictionaryAPI.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# HELPER: Render Dictionary Entry
def render_dictionary_entry(details: dict):
    if not details:
        return
        
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap;">
                <h2 style="margin: 0; font-size: 2.2rem; color: #ffffff;">{details['word']}</h2>
                <span style="color: #818cf8; font-size: 1.2rem; font-style: italic; margin-left: 10px;">
                    {details['phonetic']}
                </span>
            </div>
        """,
        unsafe_allow_html=True
    )
    
    # Play Audio if available
    if details['audio_url']:
        st.audio(details['audio_url'], format="audio/mp3")
        
    st.markdown("<hr style='border:0; height:1px; background:rgba(255,255,255,0.08); margin: 15px 0;' />", unsafe_allow_html=True)
    
    # Meanings
    for meaning in details['meanings']:
        part = meaning['partOfSpeech'].capitalize()
        st.markdown(f"<h4 style='color: #a78bfa; margin-bottom: 8px;'>{part}</h4>", unsafe_allow_html=True)
        
        for idx, d_item in enumerate(meaning['definitions']):
            d_text = d_item['definition']
            ex_text = d_item['example']
            st.markdown(
                f"""
                <div style="margin-left: 15px; margin-bottom: 12px;">
                    <p style="margin: 0; color: #e2e8f0;"><span style="color:#64748b; font-weight:600;">{idx+1}.</span> {d_text}</p>
                    {f'<p style="margin: 3px 0 0 15px; font-style: italic; color: #94a3b8; font-size: 0.95rem;">" {ex_text} "</p>' if ex_text else ''}
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # Synonyms / Antonyms
    if details['synonyms'] or details['antonyms']:
        st.markdown("<hr style='border:0; height:1px; background:rgba(255,255,255,0.08); margin: 15px 0;' />", unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            if details['synonyms']:
                syn_str = ", ".join(details['synonyms'])
                st.markdown(f"<p style='margin:0; font-size:0.9rem;'><strong style='color:#38bdf8;'>Synonyms:</strong> <span style='color:#cbd5e1;'>{syn_str}</span></p>", unsafe_allow_html=True)
        with cols[1]:
            if details['antonyms']:
                ant_str = ", ".join(details['antonyms'])
                st.markdown(f"<p style='margin:0; font-size:0.9rem;'><strong style='color:#fb7185;'>Antonyms:</strong> <span style='color:#cbd5e1;'>{ant_str}</span></p>", unsafe_allow_html=True)
                
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- MODE 1: WORD TRANSCRIBER -----------------
if mode == "🎙️ Word Transcriber":
    st.markdown(
        """
        <div class="glass-card">
            <h3>🎙️ Speech-to-Text Transcriber</h3>
            <p style="color: #cbd5e1; margin-bottom: 15px;">
                Record a word or short phrase. The AI engine will recognize your speech, display the transcript, and search for dictionary details.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Audio input element
    audio_file = st.audio_input("Record audio here")
    
    if audio_file is not None:
        # Get audio bytes
        audio_bytes = audio_file.read()
        
        with st.spinner("🎙️ Transcribing voice input..."):
            try:
                transcribed_text = speech_engine.transcribe_audio(audio_bytes)
                st.session_state.last_transcribed = transcribed_text
                
                # Add to history
                if transcribed_text not in st.session_state.transcription_history:
                    st.session_state.transcription_history.insert(0, transcribed_text)
                    
            except Exception as e:
                st.error(str(e))
                st.session_state.last_transcribed = None

    # Display results
    if st.session_state.last_transcribed:
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 5px solid #6366f1;">
                <p style="color: #818cf8; text-transform: uppercase; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.1em; margin: 0 0 5px 0;">Recognized Phrase</p>
                <h1 style="margin: 0; font-size: 2.5rem; color: #ffffff;">"{st.session_state.last_transcribed}"</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Look up definition if it's a single word
        words = st.session_state.last_transcribed.strip().split()
        if len(words) == 1:
            st.markdown("### 📖 Dictionary Look Up")
            with st.spinner(f"Searching for '{words[0]}' in dictionary..."):
                details = DictionaryAPI.get_word_details(words[0])
                if details:
                    render_dictionary_entry(details)
                else:
                    st.info(f"Could not find definitions for the word '{words[0]}' in the database.")
                    
    # History Sidebar or Bottom Section
    if st.session_state.transcription_history:
        st.markdown("### 🕒 Recent Transcriptions")
        hist_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;'>"
        for word in st.session_state.transcription_history[:10]:
            hist_html += f"<span class='status-badge' style='background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0; font-size: 0.9rem;'>{word}</span>"
        hist_html += "</div>"
        st.markdown(hist_html, unsafe_allow_html=True)


# ----------------- MODE 2: PRONUNCIATION COACH -----------------
elif mode == "🏆 Pronunciation Coach":
    st.markdown(
        """
        <div class="glass-card">
            <h3>🏆 Pronunciation Coach</h3>
            <p style="color: #cbd5e1; margin-bottom: 15px;">
                Select a word, listen to its correct pronunciation, and then record yourself saying it. Our engine will analyze your pronunciation and give you a score.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Preset words list
    categories = {
        "🟢 Easy": ["Hello", "Apple", "Welcome", "Keyboard", "Python"],
        "🟡 Medium": ["Specific", "Rural", "Phenomenon", "Squirrel", "Aesthetics"],
        "🔴 Hard": ["Prestidigitation", "Anemone", "Mischievous", "Supercalifragilisticexpialidocious", "Colonel"]
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        difficulty = st.selectbox("Choose Difficulty", list(categories.keys()))
        selected_word = st.selectbox("Select Word to Practice", categories[difficulty])
        
    with col2:
        custom_input = st.text_input("Or Enter Custom Word", placeholder="Type here...", key="custom_word_input")
        if custom_input:
            selected_word = custom_input.strip()

    # Fetch definition & audio details for target word
    with st.spinner("Loading word details..."):
        details = DictionaryAPI.get_word_details(selected_word)
        
    phonetic_display = details['phonetic'] if details and details.get('phonetic') else ""
    phonetic_text = f" <span style='color: #818cf8; font-size: 1.2rem; font-style: italic; margin-left: 10px;'>{phonetic_display}</span>" if phonetic_display else ""

    st.markdown(
        f"""
<div class="glass-card" style="text-align: center; background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.2); margin-bottom: 15px; padding-bottom: 20px;">
    <p style="color: #818cf8; text-transform: uppercase; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.15em; margin: 0 0 5px 0;">Target Word</p>
    <h1 style="margin: 0; font-size: 3.2rem; color: #ffffff; letter-spacing: 0.02em;">{selected_word.upper()}{phonetic_text}</h1>
</div>
""",
        unsafe_allow_html=True
    )
    
    # Render native audio guide
    audio_bytes = get_pronunciation_audio(selected_word)
    if audio_bytes:
        st.markdown("<p style='text-align:center; margin-bottom:5px; color:#94a3b8; font-size:0.95rem; font-weight:600;'>🎙️ Listen to Pronunciation Guide</p>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.info("Audio guide is currently unavailable for this word.")
        
    # Audio recorder
    coach_audio = st.audio_input("Record your pronunciation")
    
    if coach_audio is not None:
        audio_bytes = coach_audio.read()
        
        with st.spinner("Analyzing pronunciation..."):
            try:
                recognized_phrase = speech_engine.transcribe_audio(audio_bytes)
                
                # Similarity comparison
                score, html_diff = speech_engine.calculate_similarity(selected_word, recognized_phrase)
                
                # Styling depending on score
                if score >= 90:
                    badge_class = "badge-success"
                    badge_text = "Perfect Pronunciation!"
                    score_color = "#34d399"
                elif score >= 70:
                    badge_class = "badge-warning"
                    badge_text = "Almost Got It!"
                    score_color = "#fbbf24"
                else:
                    badge_class = "badge-danger"
                    badge_text = "Keep Practicing!"
                    score_color = "#f87171"
                # Generate custom advice based on score and target word
                advice = ""
                phonetic_guide = details['phonetic'] if details and details.get('phonetic') else ""
                
                if score >= 90:
                    advice = "🏆 <strong>Excellent job!</strong> Your pronunciation is highly accurate. Keep it up!"
                elif score >= 70:
                    advice = f"👍 <strong>Very close!</strong> Try to enunciate the syllables a bit more clearly."
                    if phonetic_guide:
                        advice += f" Follow the phonetic guide: <span style='color: #818cf8; font-weight: 600;'>{phonetic_guide}</span>."
                else:
                    advice = f"🔊 <strong>Keep practicing!</strong> Try listening to the pronunciation guide audio above again."
                    if phonetic_guide:
                        advice += f" Focus on saying the sounds: <span style='color: #818cf8; font-weight: 600;'>{phonetic_guide}</span>."
                    advice += " Make sure you are speaking clearly into the microphone."

                # Results Display
                st.markdown(
                    f"""
<div class="glass-card">
    <h4 style="margin-top:0; color:#ffffff;">Feedback Results</h4>
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
        <span class="status-badge {badge_class}">{badge_text}</span>
        <span style="font-size: 2.2rem; font-weight: 800; color: {score_color};">{score}% Match</span>
    </div>
    <div style="padding: 16px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; border-left: 5px solid {score_color};">
        <p style="margin: 0; font-size: 1.1rem; color: #e2e8f0; line-height: 1.5;">
            {advice}
        </p>
    </div>
</div>
""",
                    unsafe_allow_html=True
                )
                
            except Exception as e:
                st.error(str(e))


# ----------------- MODE 3: WORD EXPLORER -----------------
elif mode == "📖 Word Explorer":
    st.markdown(
        """
        <div class="glass-card">
            <h3>📖 Word Explorer</h3>
            <p style="color: #cbd5e1; margin-bottom: 15px;">
                Look up definitions, pronunciation audio, synonyms, and antonyms for any English word instantly.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    search_word = st.text_input("Enter a word to explore", placeholder="Type a word (e.g., 'Aesthetics', 'Ebullient', 'Exquisite')...")
    
    if search_word:
        with st.spinner(f"Fetching data for '{search_word}'..."):
            details = DictionaryAPI.get_word_details(search_word)
            if details:
                render_dictionary_entry(details)
            else:
                st.error(f"Could not find definitions for the word '{search_word}'. Make sure it's a valid English word and spelled correctly.")
