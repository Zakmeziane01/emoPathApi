import os
import glob
from dotenv import load_dotenv
import gradio as gr
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# === Load environment variables ===
load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-key-if-not-using-env')

# === Configuration ===
MODEL = "gpt-4o"
DB_NAME = "emopath_knowledge_base"
CASE_STUDY_FOLDER = "./EmoPath_KnowledgeBase/Case_Studies"

# === Load Case Studies from Folder ===
def load_case_studies(root_folder):
    """
    Load case studies from a structured folder. Each subfolder should contain:
      - triggers.txt
      - discussion_notes.txt
      - outcome.txt
    """
    case_studies = []
    for case_folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, case_folder)
        if os.path.isdir(folder_path):
            case_data = {"case_id": case_folder}
            for file_name in ["triggers.txt", "discussion_notes.txt", "outcome.txt"]:
                file_path = os.path.join(folder_path, file_name)
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        key = file_name.replace(".txt", "")
                        case_data[key] = content
                else:
                    case_data[file_name.replace(".txt", "")] = ""
            case_studies.append(case_data)
    
    print(f"✅ Loaded {len(case_studies)} case studies")
    return case_studies

# === Convert Case Studies to Langchain Documents ===
def convert_case_studies_to_documents(case_studies):
    documents = []
    for case in case_studies:
        combined_text = (
            f"Case ID: {case['case_id']}\n"
            f"Triggers: {case.get('triggers', '')}\n"
            f"Discussion Notes: {case.get('discussion_notes', '')}\n"
            f"Outcome: {case.get('outcome', '')}\n"
        )
        metadata = {"case_id": case['case_id']}
        document = Document(page_content=combined_text, metadata=metadata)
        documents.append(document)
    return documents

# === Split Documents for Efficient Embedding ===
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

# === Build AI Prompt from Retrieved Cases ===
def build_prompt_from_cases(matching_cases, query):
    """
    Construct an AI prompt by including EmoPath mission, the user query,
    and details of matching case studies.
    """
    prompt = (
        "EmoPath Mission: Support families in raising children thoughtfully with science-based, "
        "constructive alternatives to traditional punishment. Our approach encourages interactive games, "
        "visual aids, and reflective activities that foster emotional growth and positive behavior.\n\n"
    )
    prompt += f"User Query: {query}\n\nRelevant Case Studies:\n"
    
    if not matching_cases:
        prompt += "No similar case studies found. Please provide further details if available."
    else:
        for case in matching_cases:
            prompt += f"\nCase ID: {case.metadata['case_id']}\n"
            prompt += f"Content: {case.page_content}\n"
    
    prompt += (
        "\n\nBased on the above information, provide tailored, evidence-based recommendations "
        "for addressing the behavior described in the user query. Include interactive, reflective, "
        "and visual strategies where applicable."
    )
    return prompt

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
        matching_cases = retriever.invoke(question)
        prompt = build_prompt_from_cases(matching_cases, question)
        result = conversation_chain.invoke({"question": prompt})
        answer = result["answer"]
        print(f"✅ Response: {answer}")
        return answer
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Sorry, I couldn’t process that request. Please try again."

# === Load and Process Knowledge Base ===
case_studies = load_case_studies(CASE_STUDY_FOLDER)
documents = convert_case_studies_to_documents(case_studies)
chunks = split_documents(documents)

# === Use OpenAI or HuggingFace Embeddings ===
# Option 1: OpenAI Embeddings (More accurate but paid)
embeddings = OpenAIEmbeddings()

# Option 2: HuggingFace (Free, but may require GPU)
# from langchain.embeddings import HuggingFaceEmbeddings
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = setup_vector_store(chunks)
conversation_chain = setup_model_and_retriever(vector_store)
retriever = vector_store.as_retriever()

# === Gradio Chat Interface ===
chat_interface = gr.ChatInterface(chat, type="messages")
chat_interface.launch(inbrowser=True)
