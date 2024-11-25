from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
import retriever
from pinecone import Pinecone
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

PINECONE_API_KEY="pcsk_44GEVQ_MUe9BzErbdfazWZQa2UWAmEapM83rLJJbHTc6fkdiQEj2o6JS7mNCvTY25XF3X9"

pc = Pinecone(PINECONE_API_KEY)

def get_response(user_query):
    indexes = pc.list_indexes()
    print('****INDEXES*****:',indexes)
    context = retriever.retrieve_from_pinecone(user_query)[:5]
    print(context)
    st.session_state.context_log = [context]
    
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    template = """
        Answer the question below according to your knowledge in a way that will be helpful to people potentially starting nonprofits asking the question.
        The following context is your only source of knowledge to answer from. Be direct in your answers. Act like you know what you are talking about.
        Context: {context}
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
if "context_log" not in st.session_state:
    st.session_state.context_log = ["Retrieved context will be displayed here"]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="Hi there! Welcome to the Center for Nonprofit Management's Resource Chatbot. How can I assist you today?")]

with st.sidebar:
    st.image("cnm-logo.svg")  
    st.title("About Center for Nonprofit Management")
    st.markdown(
        """The [Center for Nonprofit Management](https://cnmsocal.org/) (CNM) is a non-profit organization that provides
        resources and support to non-profit organizations in Southern California. They offer training,
        consulting, and other services to help non-profits achieve their goals and stay sustainable.
        CNM's mission is to promote the growth and development of non-profit organizations
        through education, collaboration, and advocacy."""
    )

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)


user_query = st.chat_input("Ask us your question here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
    
    with st.chat_message("AI"):
        response = st.write_stream(get_response(user_query))
    
    st.session_state.chat_history.append(AIMessage(content=response))