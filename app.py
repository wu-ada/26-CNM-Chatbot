import streamlit as st

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
import retriever
from pinecone import Pinecone

from gtts import gTTS
import warnings
import tempfile
import os
from deep_translator import GoogleTranslator
import csv
import speech_recognition as sr


warnings.filterwarnings('ignore')

PINECONE_API_KEY=st.secrets["PINECONE_API_KEY"]
# PINECONE_API_KEY="pcsk_44GEVQ_MUe9BzErbdfazWZQa2UWAmEapM83rLJJbHTc6fkdiQEj2o6JS7mNCvTY25XF3X9"

pc = Pinecone(PINECONE_API_KEY)

def get_response(user_query):
    indexes = pc.list_indexes()
    print('****INDEXES*****:',indexes)
    context = retriever.retrieve_from_pinecone(user_query)[:5]
    print(context)
    st.session_state.context_log = [context]
   
    llm = ChatOllama(model="tinyllama", temperature=0)
   
    template = """
        Answer the question below according to the given context in a way that will be helpful to people potentially starting nonprofits asking the question(users of the chatbot).
        The following context is you (the chatbot's) only source of knowledge to answer from. The chatbot's answers should be direct.
        The chatbot is speaking on behalf of CNM (Center for Nonprofit Management). The chatbot should act like it knows what it is talking about. If
        the chatbot is given a query it does not know the answer to, it will tell the user that that information is behind a paywall, and that the user
        can look into CNM's services for more, and direct them to this link: https://cnmsocal.org. At the end of your answer, please also provide the
        exact name of the document file within the provided pinecone database or exact link on the website that you got this information from.
        User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()




    response = chain.stream({
        "context": context,
        "user_question": user_query
    })
   
    # Extract the best-matching reference for scoring
    reference = context[0] if context else ""
   

    st.session_state.response_log = response
   
    return response




if "context_log" not in st.session_state:
    st.session_state.context_log = ["Retrieved context will be displayed here"]




# Initialize the Google Translator

# Simplified translation function
def translate(text):
    translation = GoogleTranslator(source='auto', target=language_code).translate(text)
    return translation

# Dictionary of languages in their native forms with corresponding ISO codes
languages = {
    "en": "English",
    "es": "Español (Spanish)",
    "zh-CN": "中文 (简体) (Chinese Simplified)",
    "af": "Afrikaans",
    "sq": "Shqip (Albanian)",
    "am": "አማርኛ (Amharic)",
    "ar": "العربية (Arabic)",
    "hy": "Հայերեն (Armenian)",
    "as": "অসমীয়া (Assamese)",
    "ay": "Aymara",
    "az": "Azərbaycan (Azerbaijani)",
    "bm": "Bamanankan (Bambara)",
    "eu": "Euskara (Basque)",
    "be": "Беларуская (Belarusian)",
    "bn": "বাংলা (Bengali)",
    "bho": "Bhojpuri",
    "bs": "Bosanski (Bosnian)",
    "bg": "Български (Bulgarian)",
    "ca": "Català (Catalan)",
    "ceb": "Cebuano",
    "ny": "Chichewa",
    "zh-TW": "中文 (繁體) (Chinese Traditional)",
    "co": "Corsu (Corsican)",
    "hr": "Hrvatski (Croatian)",
    "cs": "Čeština (Czech)",
    "da": "Dansk (Danish)",
    "dv": "Divehi",
    "doi": "Dogri",
    "nl": "Nederlands (Dutch)",
    "eo": "Esperanto",
    "et": "Eesti (Estonian)",
    "ee": "Eʋegbe (Ewe)",
    "tl": "Filipino",
    "fi": "Suomi (Finnish)",
    "fr": "Français (French)",
    "fy": "Fries (Frisian)",
    "gl": "Galego (Galician)",
    "ka": "ქართული (Georgian)",
    "de": "Deutsch (German)",
    "el": "Ελληνικά (Greek)",
    "gn": "Aña Guarani (Guarani)",
    "gu": "ગુજરાતી (Gujarati)",
    "ht": "Kreyòl Ayisyen (Haitian Creole)",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "iw": "עברית (Hebrew)",
    "hi": "हिन्दी (Hindi)",
    "hmn": "Hmong",
    "hu": "Magyar (Hungarian)",
    "is": "Íslenska (Icelandic)",
    "ig": "Igbo",
    "ilo": "Ilokano (Ilocano)",
    "id": "Bahasa Indonesia (Indonesian)",
    "ga": "Gaeilge (Irish)",
    "it": "Italiano (Italian)",
    "ja": "日本語 (Japanese)",
    "jw": "Basa Jawa (Javanese)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "kk": "Қазақ тілі (Kazakh)",
    "km": "ភាសាខ្មែរ (Khmer)",
    "rw": "Ikinyarwanda (Kinyarwanda)",
    "gom": "Konkani",
    "ko": "한국어 (Korean)",
    "kri": "Krio",
    "ku": "Kurdî (Kurdish Kurmanji)",
    "ckb": "کوردی (Kurdish Sorani)",
    "ky": "Кыргызча (Kyrgyz)",
    "lo": "ລາວ (Lao)",
    "la": "Latina (Latin)",
    "lv": "Latviešu (Latvian)",
    "ln": "Lingála (Lingala)",
    "lt": "Lietuvių (Lithuanian)",
    "lg": "Luganda",
    "lb": "Lëtzebuergesch (Luxembourgish)",
    "mk": "Македонски (Macedonian)",
    "mai": "मैथिली (Maithili)",
    "mg": "Malagasy",
    "ms": "Melayu (Malay)",
    "ml": "മലയാളം (Malayalam)",
    "mt": "Malti (Maltese)",
    "mi": "Māori (Maori)",
    "mr": "मराठी (Marathi)",
    "mni-Mtei": "Meitei (Manipuri)",
    "lus": "Mizo",
    "mn": "Монгол (Mongolian)",
    "my": "မြန်မာ (Myanmar)",
    "ne": "नेपाली (Nepali)",
    "no": "Norsk (Norwegian)",
    "or": "ଓଡ଼ିଆ (Odia)",
    "om": "Oromo",
    "ps": "پښتو (Pashto)",
    "fa": "فارسی (Persian)",
    "pl": "Polski (Polish)",
    "pt": "Português (Portuguese)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)",
    "qu": "Quechua",
    "ro": "Română (Romanian)",
    "ru": "Русский (Russian)",
    "sm": "Samoan",
    "sa": "संस्कृत (Sanskrit)",
    "gd": "Gàidhlig (Scots Gaelic)",
    "nso": "Sepedi",
    "sr": "Српски (Serbian)",
    "st": "Sesotho",
    "sn": "Shona",
    "sd": "سنڌي (Sindhi)",
    "si": "සිංහල (Sinhala)",
    "sk": "Slovenčina (Slovak)",
    "sl": "Slovenščina (Slovenian)",
    "so": "Soomaali (Somali)",
    "su": "Basa Sunda (Sundanese)",
    "sw": "Kiswahili (Swahili)",
    "sv": "Svenska (Swedish)",
    "tg": "Тоҷикӣ (Tajik)",
    "ta": "தமிழ் (Tamil)",
    "tt": "Татарча (Tatar)",
    "te": "తెలుగు (Telugu)",
    "th": "ไทย (Thai)",
    "ti": "ትግርኛ (Tigrinya)",
    "ts": "Xitsonga (Tsonga)",
    "tr": "Türkçe (Turkish)",
    "tk": "Türkmençe (Turkmen)",
    "ak": "Twi",
    "uk": "Українська (Ukrainian)",
    "ur": "اردو (Urdu)",
    "ug": "ئۇيغۇرچە (Uyghur)",
    "uz": "O'zbekcha (Uzbek)",
    "vi": "Tiếng Việt (Vietnamese)",
    "cy": "Cymraeg (Welsh)",
    "xh": "isiXhosa (Xhosa)",
    "yi": "ייִדיש (Yiddish)",
    "yo": "Yorùbá (Yoruba)",
    "zu": "Zulu"
}

with st.sidebar:
    st.image("cnm-logo.svg")
    
    # Language selection
    user_language = st.selectbox("Select your preferred language", list(languages.values()))
    language_code = list(languages.keys())[list(languages.values()).index(user_language)]

    greeting = translate("Hi there! Welcome to the Center for Nonprofit Management's Resource Chatbot. How can I assist you today?")
            
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [AIMessage(content=greeting)]
        
    if AIMessage(greeting) not in st.session_state.chat_history:
        st.session_state.chat_history =[AIMessage(content=greeting)]
                
    #Text to speech selection
    text_to_speech_choice = st.selectbox(translate("Activate text to speech?"), list([translate("No"), translate("Yes")]))
    
    additional_resources = st.sidebar.selectbox(translate("Additional Resources"), [translate("About CNM"), translate("Talk to an Employee"), translate("View All Resources")])
    
    # Display additional resource based on selection
    if additional_resources == translate("About CNM"):
        translated_sidebar_title = translate("About Center for Nonprofit Management")
        st.title(translated_sidebar_title)
        about = """The Center for Nonprofit Management (CNM) is a non-profit organization that provides
            resources and support to non-profit organizations in Southern California. They offer training,
            consulting, and other services to help non-profits achieve their goals and stay sustainable.
            CNM's mission is to promote the growth and development of non-profit organizations
            through education, collaboration, and advocacy. To learn more, visit https://cnmsocal.org/."""
        translated_about = translate(about)
        st.markdown(translated_about)
    elif additional_resources == translate("Talk to an Employee"):
        
        with st.form(key="user_form", clear_on_submit=True):
            translated_title = translate("Please fill out the form below with any extra questions/comments:")
            st.write(translated_title)
            # Define the fieldnames for the CSV
            fieldnames = ['first_name', 'last_name', 'email', 'subject', 'message']
            
            translated_first_name = translate("First Name*")
            translated_last_name = translate("Last Name*")
            translated_email = translate("Email*")
            translated_subject= translate("Subject*")
            translated_message = translate("Message*")
            translated_submit_button = translate("Submit")
            translated_success = translate("Your response has been saved!")
            translated_error = translate("Please fill out all fields.")
            translated_download = translate("Download CSV")
            translated_required = translate('<p style="font-size: 13px;">*Required fields</p>')

            first_name = st.text_input(translated_first_name)
            last_name = st.text_input(translated_last_name)
            email = st.text_input(translated_email)
            subject = st.text_input(translated_subject)
            message = st.text_area(translated_message)
            st.markdown(translated_required, unsafe_allow_html=True)

            # Submit button
            submit_button = st.form_submit_button(label=translated_submit_button)

            # after form is submitted, the datais stored in the CSV file
            if submit_button:
                if first_name and last_name and email and subject and message:
                    # Append the data to the CSV file
                    with open('responses.csv', mode='a', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        # Write the header only once, if file is empty
                        if file.tell() == 0:
                            writer.writeheader()
                        writer.writerow({
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'subject': subject,
                            'message': message
                        })
                    st.success(translated_success)
                else:
                    st.error(translated_error)
    
           
        import pandas as pd

        # Read the CSV with saved questions
        df = pd.read_csv('responses.csv')

        # Converts DataFrame to CSV format for download
        csv = df.to_csv(index=False)

        # download the CSV
        st.download_button(
            label=translated_download,
            data=csv,
            file_name='responses.csv',
            mime='text/csv'
        )

    elif additional_resources == translate("View All Resources"):
        # Set the folder path
        folder_path = os.path.join(os.getcwd(), "Data")

        # List all files in the folder
        files = os.listdir(folder_path)

        # Filter to include only documents (optional)
        document_files = [f for f in files if f.endswith(('.pdf', '.docx', '.txt'))]  

        # Display file names and provide download buttons
        for file_name in document_files:            
            # Full path to the file
            file_path = os.path.join(folder_path, file_name)
            # Allow the user to download the file
            with open(file_path, "rb") as file:
                st.download_button(
                    label=f"{translate(file_name)}",
                    data=file,
                    file_name=file_name,
                    mime="application/octet-stream"
                )

translated_title = translate("CNM Chatbot")
st.image("cnm-page-header.png")  
st.title(translated_title)


def text_to_speech(text):
    """Convert text to speech using gTTS and save it to a temporary file."""
    tts = gTTS(text=text, lang=language_code)
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name

def play_audio_on_response(response_text):
    if text_to_speech_choice == translate("Yes"):
                translated_button = translate("Play Audio")
                if st.button(translated_button, key=f"play_{response_text[:10]}"):
                    audio_file = text_to_speech(response_text)
                    st.audio(audio_file, format="audio/mp3")
                    os.remove(audio_file)  # Clean up after playing
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            with st.spinner(translate("Loading...")):
                st.write(message.content)
            # Add a button to play the audio
            # if text_to_speech_choice == translate("Yes"):
            #     translated_button = translate("Play Audio")
            #     if st.button(translated_button, key=f"play_{message.content[:10]}"):
                play_audio_on_response(message.content)
                    # audio_file = text_to_speech(message.content)
                    # st.audio(audio_file, format="audio/mp3")
                    # os.remove(audio_file)  # Clean up temporary file after playback
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

question = translate("Ask us a question here...")
user_query = st.chat_input(question)
    
if user_query is not None and user_query != "":
    with st.chat_message("Human"):
        st.markdown(user_query)
    
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    english_query = GoogleTranslator(source='auto', target='en').translate(user_query)
    
    with st.chat_message("AI"):
        with st.spinner(translate("Loading...")):

            response = get_response(english_query)
            # Capture the complete response from the stream
            full_response = ""
            for part in response:
                full_response += part  # Collect all parts
            translated_response = translate(full_response)
            st.write(f"{translated_response}")
            play_audio_on_response(translated_response)
    
    st.session_state.chat_history.append(AIMessage(content=translated_response))
    













# import streamlit as st

# st.set_page_config(
#     page_title="TESTING",
#     page_icon="cnm-icon.png",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://www.extremelycoolapp.com/help',
#         'Report a bug': "https://www.extremelycoolapp.com/bug",
#         'About': "# This is a header. This is an *extremely* cool app!"
#     }
# )
# pages = {
#     "Home": [
#         st.Page("code.py", title="Chat with chatbot"),
#         # st.Page("manage_account.py", title="Manage your account"),
#     ],
#     "Resources": [
#         # st.Page("code.py", title="Learn about us"),
#         st.Page("ask.py", title="Ask questions"),
#     ],
# }

# pg = st.navigation(pages)
# pg.run()
