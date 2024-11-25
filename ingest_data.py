from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

import os
from pinecone import Pinecone
import warnings
warnings.filterwarnings('ignore')


PINECONE_API_KEY="pcsk_44GEVQ_MUe9BzErbdfazWZQa2UWAmEapM83rLJJbHTc6fkdiQEj2o6JS7mNCvTY25XF3X9"
# Load sentence transformer model for embedding
embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

# Initialize Pinecone with API key
pc = Pinecone(api_key=PINECONE_API_KEY)
# Define Pinecone index
index_name = "test"
index = pc.Index(index_name)
# Print index statistics
index.describe_index_stats()

# Load the PDF document

loader = PyPDFDirectoryLoader("data")
data = loader.load()
print("done loading")
# Split the document into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
fragments = text_splitter.split_documents(data)
# Print a sample of the text fragments

# Convert fragments into embeddings and store in Pinecone
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
vectorstore.add_documents(fragments)

