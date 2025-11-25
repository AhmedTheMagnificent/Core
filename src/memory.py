from importlib.metadata import metadata
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

vector_store = Chroma(
    collection_name="core_knowledge",
    embedding_function=embeddings,
    persist_directory="./core_db"
)

def save_to_memory(text: str, source: str = "user"):
    print(f"   [Memory] Saving: '{text[:30]}...'")
    
    doc = Document(
        page_content=text,
        metadata={"source": source}
    )
    vector_store.add_documents([doc])
    
def recall_memory(query: str, n_results: int = 2):
    print(f"   [Memory] Searching for relevant info to: '{query}'")
    
    results = vector_store.similarity_search(query, k=n_results)
    return [doc.page_content for doc in results]