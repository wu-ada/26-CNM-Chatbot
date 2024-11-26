import streamlit as st
from gtts import gTTS
import tempfile
import os

def text_to_speech(text, lang='en'):
    """Convert text to speech using gTTS and save it to a temporary file."""
    tts = gTTS(text=text, lang=lang)
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name

# Streamlit app setup
st.set_page_config(page_title="Audio Player", layout="wide")
st.title("Text to Audio Converter")

user_input = st.text_input("Enter text to convert to speech:")

if st.button("Play Audio"):
    if user_input:
        audio_file = text_to_speech(user_input)  # Generate the audio
        # Use HTML to autoplay the audio
        st.markdown(f"""
            <audio id="audio" src="{audio_file}" autoplay></audio>
            <script>
                document.getElementById('audio').play();
            </script>
        """, unsafe_allow_html=True)

        # Clean up the temporary audio file
        os.remove(audio_file)  # Optionally delay this removal if needed
    else:
        st.error("Please enter text to convert.")