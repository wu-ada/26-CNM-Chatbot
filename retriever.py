from langchain_pinecone import vectorstores
from langchain_community.embeddings import SentenceTransformerEmbeddings
from pinecone import Pinecone
import os
import warnings
warnings.filterwarnings('ignore')

PINECONE_API_KEY="pcsk_44GEVQ_MUe9BzErbdfazWZQa2UWAmEapM83rLJJbHTc6fkdiQEj2o6JS7mNCvTY25XF3X9" # available at app.pinecone.io

embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
pc = Pinecone(PINECONE_API_KEY)

def retrieve_from_pinecone(user_query="What information do you have on Instance Sync Permissions"):
    index_name = "test"
    index = pc.Index(index_name)
    
    print("Index stats:", index.describe_index_stats())
    
    pinecone = vectorstores.Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
    context = pinecone.similarity_search(user_query)[:5]
    
    return context