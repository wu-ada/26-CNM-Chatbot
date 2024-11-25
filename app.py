from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
import retriever
from pinecone import Pinecone
import streamlit as st
from gtts import gTTS
import warnings
import tempfile
import os
from googletrans import Translator
warnings.filterwarnings('ignore')

PINECONE_API_KEY="pcsk_44GEVQ_MUe9BzErbdfazWZQa2UWAmEapM83rLJJbHTc6fkdiQEj2o6JS7mNCvTY25XF3X9"

pc = Pinecone(PINECONE_API_KEY)

def text_to_speech(text):
    """Convert text to speech using gTTS and save it to a temporary file."""
    tts = gTTS(text=text, lang='en')
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name

def get_response(user_query):
    indexes = pc.list_indexes()
    print('****INDEXES*****:',indexes)
    context = retriever.retrieve_from_pinecone(user_query)[:5]
    print(context)
    st.session_state.context_log = [context]
    
    llm = ChatOllama(model="tinyllama", temperature=0)
    
    template = """
        Answer the question below according to the given context in a way that will be helpful to people potentially starting nonprofits asking the question(users of the chatbot).
        The following context is you(the chatbot's) only source of knowledge to answer from. The chatbot's answers should be direct. The chatbot is speaking on behalf of CNM (Center for Nonprofit Management). The chatbot should act like it knows what it is talking about. If
        the chatbot is given a query it does not know the answer to, it will tell the user that that information is behind a paywall, and that the user
        can look into CNM's services for more, and direct them to this link: https://cnmsocal.org
         User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "context": context,
        "user_question": user_query
    })
    
st.set_page_config(page_title="CNM Chatbot", page_icon="cnm-icon.png", layout="wide")
st.image("cnm-page-header.png")  
st.title("CNM Chatbot")

# Dictionary of languages in their native forms with corresponding ISO codes
languages = {
    "en": "English",
    "es": "Español (Spanish)",
    "zh-cn": "简体中文 (Simplified Chinese)",
    "af": "Afrikaans",
    "sq": "Shqip (Albanian)",
    "am": "አማርኛ (Amharic)",
    "ar": "العربية (Arabic)",
    "hy": "Հայերեն (Armenian)",
    "eu": "Euskara (Basque)",
    "bn": "বাংলা (Bengali)",
    "bg": "Български (Bulgarian)",
    "ca": "Català (Catalan)",
    "zh-tw": "繁體中文 (Traditional Chinese)",
    "hr": "Hrvatski (Croatian)",
    "cs": "Česky (Czech)",
    "da": "Dansk (Danish)",
    "nl": "Nederlands (Dutch)",
    "et": "Eesti (Estonian)",
    "el": "Ελληνικά (Greek)",
    "fa": "فارسی (Persian)",
    "fi": "Suomi (Finnish)",
    "fr": "Français (French)",
    "de": "Deutsch (German)",
    "gu": "ગુજરાતી (Gujarati)",
    "hi": "हिंदी (Hindi)",
    "hu": "Magyar (Hungarian)",
    "id": "Indonesia (Indonesian)",
    "it": "Italiano (Italian)",
    "ja": "日本語 (Japanese)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ko": "한국어 (Korean)",
    "lt": "Lietuvių (Lithuanian)",
    "lv": "Latviešu (Latvian)",
    "mk": "Македонски (Macedonian)",
    "ml": "മലയാളം (Malayalam)",
    "mr": "मराठी (Marathi)",
    "no": "Norsk (Norwegian)",
    "pl": "Polski (Polish)",
    "pt": "Português (Portuguese)",
    "ro": "Română (Romanian)",
    "ru": "Русский (Russian)",
    "sr": "Српски (Serbian)",
    "si": "සිංහල (Sinhalese)",
    "sk": "Slovenský (Slovak)",
    "sl": "Slovenščina (Slovenian)",
    "sv": "Svenska (Swedish)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "th": "ไทย (Thai)",
    "tr": "Türkçe (Turkish)",
    "uk": "Українська (Ukrainian)",
    "vi": "Tiếng Việt (Vietnamese)",
    "cy": "Cymraeg (Welsh)",
    "ga": "Gaeilge (Irish)",
    "eo": "Wêreldtaal (Esperanto)",
}

if "context_log" not in st.session_state:
    st.session_state.context_log = ["Retrieved context will be displayed here"]

with st.sidebar:
    st.image("cnm-logo.svg")
    
    # Initialize the Google Translator
    translator = Translator()
    # Language selection
    user_language = st.selectbox("Select your preferred language", list(languages.values()))
    language_code = list(languages.keys())[list(languages.values()).index(user_language)]
    translated_activate_text = translator.translate("Activate text to speech?", dest=language_code).text
    translated_yes = translator.translate("Yes", dest=language_code).text
    translated_no = translator.translate("No", dest=language_code).text
    text_to_speech_choice = st.selectbox(translated_activate_text, list([translated_yes, translated_no]))
    
    greeting = translator.translate("Hi there! Welcome to the Center for Nonprofit Management's Resource Chatbot. How can I assist you today?", dest=language_code).text
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [AIMessage(content=greeting)]

    st.title("About Center for Nonprofit Management")
    about = """The Center for Nonprofit Management (CNM) is a non-profit organization that provides
        resources and support to non-profit organizations in Southern California. They offer training,
        consulting, and other services to help non-profits achieve their goals and stay sustainable.
        CNM's mission is to promote the growth and development of non-profit organizations
        through education, collaboration, and advocacy. To learn more, visit https://cnmsocal.org/."""
    translated_about = translator.translate(about, dest=language_code).text
    st.markdown(translated_about)

def text_to_speech(text):
    """Convert text to speech using gTTS and save it to a temporary file."""
    tts = gTTS(text=text, lang=language_code)
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
            # Add a button to play the audio
            if text_to_speech_choice == translated_yes:
                translated_button = translator.translate("Play Audio", dest=language_code).text
                if st.button(translated_button, key=f"play_{message.content[:10]}"):
                    audio_file = text_to_speech(message.content)
                    st.audio(audio_file, format="audio/mp3")
                    os.remove(audio_file)  # Clean up temporary file after playback
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

question = translator.translate("Ask us a question here...", dest=language_code).text
user_query = st.chat_input(question)
    
if user_query is not None and user_query != "":
    with st.chat_message("Human"):
        st.markdown(user_query)
    
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    english_query = translator.translate(user_query, dest='en').text
    
    with st.chat_message("AI"):
        response = get_response(english_query)
        # Capture the complete response from the stream
        full_response = ""
        for part in response:
            full_response += part  # Collect all parts
        translated_response = translator.translate(full_response, dest=language_code).text
        st.write(f"{translated_response}")
    
    st.session_state.chat_history.append(AIMessage(content=translated_response))