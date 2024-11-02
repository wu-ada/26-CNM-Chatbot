import streamlit as st
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

# Page config
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")
st.title("Center for Nonprofit Management Resource Chatbot")

# Sidebar for model selection
with st.sidebar:
    st.title("Model Settings")
    model_option = st.selectbox(
        'Choose LLM Provider',
        ('Ollama', 'OpenAI')
    )
    
    if model_option == 'OpenAI':
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        openai_model = st.selectbox(
            'Choose OpenAI Model',
            ('gpt-3.5-turbo', 'gpt-4')
        )
        if not openai_api_key:
            st.warning('Please enter your OpenAI API key', icon='⚠️')
    else:
        ollama_model = st.selectbox(
            'Choose Ollama Model',
            ('llama3.1', 'mistral', 'gemma', 'tinyllama')  # Add any other models you have in Ollama
        )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_llm():
    """Get the appropriate LLM based on user selection"""
    if model_option == 'OpenAI':
        if not openai_api_key:
            st.error("Please enter an OpenAI API key!")
            st.stop()
        os.environ["OPENAI_API_KEY"] = openai_api_key
        return OpenAI(model=openai_model, temperature=0.7)
    else:
        return Ollama(model=ollama_model, request_timeout=120.0)

@st.cache_resource
def initialize_rag(_llm):
    """Initialize the RAG pipeline components"""
    # Configure settings
    Settings.llm = _llm
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    # Load and index documents
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    return index

def generate_response(prompt: str, index):
    """Generate streaming response from RAG query"""
    query_engine = index.as_query_engine(
        streaming=True,
        similarity_top_k=1
    )
    response = query_engine.query(prompt)
    
    # Yield each token from the streaming response
    for text in response.response_gen:
        yield text

# Get LLM and initialize RAG system
llm = get_llm()

# Create a button to reinitialize the index with new settings
if st.sidebar.button("Reinitialize with Selected Model"):
    st.cache_resource.clear()
    st.session_state.messages = []  # Optional: clear chat history
    st.rerun()

try:
    index = initialize_rag(llm)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response = st.write_stream(generate_response(prompt, index))
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

except Exception as e:
    st.error(f"Error: {str(e)}")
    if model_option == 'Ollama':
        st.info("If using Ollama, make sure the Ollama server is running and the selected model is installed.")

# Display current model info in sidebar
with st.sidebar:
    st.divider()
    st.subheader("Current Settings")
    st.write(f"Provider: {model_option}")
    if model_option == 'OpenAI':
        st.write(f"Model: {openai_model}")
    else:
        st.write(f"Model: {ollama_model}")