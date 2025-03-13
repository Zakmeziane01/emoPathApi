import os
import glob
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# Load environment variables
load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

# === Configuration ===
MODEL = "gpt-4o-mini"  # Low-cost, high-efficiency model
DB_NAME = "parenting_knowledge_base"

# === Load Documents ===
def load_documents():
    folders = glob.glob("knowledge-base/*")
    text_loader_kwargs = {'encoding': 'utf-8'}

    documents = []
    for folder in folders:
        doc_type = os.path.basename(folder)
        loader = DirectoryLoader(
            folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs
        )
        folder_docs = loader.load()
        for doc in folder_docs:
            doc.metadata["doc_type"] = doc_type
        documents.extend(folder_docs)
    
    print(f"✅ Loaded {len(documents)} documents")
    return documents

# === Split Text into Chunks ===
def split_documents(documents):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks

# === Create or Load Vector Store ===
def setup_vector_store(chunks):
    if os.path.exists(DB_NAME):
        print("🗑️ Existing database found. Deleting...")
        Chroma(persist_directory=DB_NAME, embedding_function=embeddings).delete_collection()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_NAME
    )
    
    print(f"✅ Vector store created with {vector_store._collection.count()} documents")
    return vector_store

# === Setup Model and Retriever ===
def setup_model_and_retriever(vector_store):
    llm = ChatOpenAI(temperature=0.7, model_name=MODEL)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    retriever = vector_store.as_retriever()

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory
    )
    
    return conversation_chain

# === Handle User Queries ===
def chat(question, history):
    print(f"🤖 User asked: {question}")
    try:
        result = conversation_chain.invoke({"question": question})
        answer = result["answer"]
        print(f"✅ Response: {answer}")
        return answer
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Sorry, I couldn’t process that request. Please try again."

# === Load and Process Knowledge Base ===
documents = load_documents()
chunks = split_documents(documents)

# === Use OpenAI or HuggingFace Embeddings ===
# Option 1: OpenAI (More accurate but paid)
embeddings = OpenAIEmbeddings()

# Option 2: HuggingFace (Free, but may require GPU for large datasets)
# from langchain.embeddings import HuggingFaceEmbeddings
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = setup_vector_store(chunks)
conversation_chain = setup_model_and_retriever(vector_store)
