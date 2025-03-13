from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.schema import Document

# === Load environment variables ===
load_dotenv(override=True)
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# === Configuration ===
MODEL = "gpt-4o"
DB_NAME = "emopath_knowledge_base"
CASE_STUDY_FOLDER = "./EmoPath_KnowledgeBase/Case_Studies"

# === FastAPI Models ===
class FamilyData(BaseModel):
    parent: Optional[Dict[str, Any]] = None
    children: Optional[List[Dict[str, Any]]] = []

class RAGResponse(BaseModel):
    message: str
    recommendations: str
    matched_cases: List[str] = []

# === RAG System Functions ===
def load_case_studies(root_folder):
    try:
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
        print(f"Loaded {len(case_studies)} case studies.")
        return case_studies
    except Exception as e:
        print(f"Error loading case studies: {str(e)}")
        return []

def convert_to_documents(case_studies):
    documents = []
    for case in case_studies:
        content = (
            f"Case ID: {case['case_id']}\n"
            f"Triggers: {case.get('triggers', '')}\n"
            f"Discussion Notes: {case.get('discussion_notes', '')}\n"
            f"Outcome: {case.get('outcome', '')}\n"
        )
        doc = Document(page_content=content, metadata={"case_id": case['case_id']})
        documents.append(doc)
    return documents

def split_documents(documents):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def setup_vector_store(chunks):
    try:
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=DB_NAME
        )
        print(f"Vector store created with {vector_store._collection.count()} documents")
        return vector_store
    except Exception as e:
        print(f"Error setting up vector store: {str(e)}")
        raise

def extract_family_context(data_info):
    """Extract relevant information from family data to create a query context"""
    context = ""
    
    # Extract parent information
    if data_info.get("parent"):
        parent = data_info["parent"]
        context += "Parent Information:\n"
        if parent.get("firstName") and parent.get("lastName"):
            context += f"Name: {parent.get('firstName')} {parent.get('lastName')}\n"
        if parent.get("parentingChallenges"):
            context += f"Parenting Challenges: {parent.get('parentingChallenges')}\n"
        if parent.get("familyDynamics"):
            context += f"Family Dynamics: {parent.get('familyDynamics')}\n"
    
    # Extract children information
    if data_info.get("children") and len(data_info["children"]) > 0:
        context += "\nChildren Information:\n"
        for i, child in enumerate(data_info["children"]):
            context += f"Child {i+1}:\n"
            if child.get("name"):
                context += f"Name: {child.get('name')}\n"
            if child.get("age"):
                context += f"Age: {child.get('age')}\n"
            if child.get("gender"):
                context += f"Gender: {child.get('gender')}\n"
            if child.get("grade"):
                context += f"Grade: {child.get('grade')}\n"
            if child.get("childStrengths"):
                context += f"Strengths: {child.get('childStrengths')}\n"
            if child.get("childCurrentChallenges"):
                context += f"Current Challenges: {child.get('childCurrentChallenges')}\n"
            if child.get("recentBehavior"):
                context += f"Recent Behavior: {child.get('recentBehavior')}\n"
            if child.get("behaviorTriggers"):
                context += f"Behavior Triggers: {child.get('behaviorTriggers')}\n"
            if child.get("ChildRulesReaction"):
                context += f"Reaction to Rules: {child.get('ChildRulesReaction')}\n"
    
    return context

def build_prompt(matching_cases, family_context):
    prompt = (
        "EmoPath Mission: Support families in raising children thoughtfully with science-based, "
        "constructive alternatives to traditional punishment. Our approach encourages interactive games, "
        "visual aids, and reflective activities that foster emotional growth and positive behavior.\n\n"
        f"Family Context:\n{family_context}\n\n"
        f"Relevant Case Studies:\n"
    )

    if not matching_cases:
        prompt += "No similar case studies found in our database yet. Providing general recommendations based on available information."
    else:
        for case in matching_cases:
            prompt += f"\n--- Case ID: {case.metadata['case_id']} ---\n"
            prompt += f"Triggers: {case.page_content.split('Triggers: ')[1].split('\n')[0]}\n"
            prompt += f"Discussion: {case.page_content.split('Discussion Notes: ')[1].split('\n')[0]}\n"
            prompt += f"Outcome: {case.page_content.split('Outcome: ')[1].split('\n')[0]}\n"

    prompt += (
        "\n\nBased on the above information, provide tailored, evidence-based recommendations "
        "for this family. Include:\n"
        "1. A personalized greeting and acknowledgment of their specific situation\n"
        "2. 3-5 specific, practical strategies they can implement immediately\n"
        "3. Interactive, reflective, and visual activities tailored to the child's age and development\n"
        "4. A supportive closing message that encourages continued engagement with EmoPath\n\n"
        "Format your response in a warm, supportive tone that empowers parents rather than criticizing."
    )
    return prompt

def generate_response(prompt):
    try:
        llm = ChatOpenAI(temperature=0.7, model_name=MODEL)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return "We're experiencing technical difficulties. Please try again later."

def extract_case_ids(matching_cases):
    """Extract case IDs from matching cases for response metadata"""
    return [case.metadata.get('case_id') for case in matching_cases if case.metadata.get('case_id')]

def rag_system_omf(data_info):
    try:
        # Load and prepare case studies
        case_studies = load_case_studies(CASE_STUDY_FOLDER)
        documents = convert_to_documents(case_studies)
        chunks = split_documents(documents)
        vector_store = setup_vector_store(chunks)
        
        # Extract family context to use as query
        family_context = extract_family_context(data_info)
        
        # If we don't have enough context, return a prompt for more information
        if len(family_context.strip()) < 20:
            return RAGResponse(
                message="We need more information about your family to provide personalized guidance.",
                recommendations="Please complete more fields in your profile, particularly about parenting challenges, family dynamics, and your child's behavior patterns.",
                matched_cases=[]
            )
        
        # Search for relevant case studies
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 most relevant cases
        matching_cases = retriever.invoke(family_context)
        
        # Build prompt and generate response
        prompt = build_prompt(matching_cases, family_context)
        ai_response = generate_response(prompt)
        
        # Extract case IDs for metadata
        case_ids = extract_case_ids(matching_cases)
        
        return RAGResponse(
            message="Personalized guidance generated successfully",
            recommendations=ai_response,
            matched_cases=case_ids
        )
    except Exception as e:
        print(f"Error in RAG system: {str(e)}")
        return RAGResponse(
            message="An error occurred while processing your request",
            recommendations="We apologize for the inconvenience. Our team has been notified of this issue.",
            matched_cases=[]
        )