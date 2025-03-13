import os

def load_case_studies(root_folder):
    """
    Load EmoPath case studies from the given folder. Each subfolder should represent one case study
    (e.g., Case_001, Case_002, etc.) containing:
      - triggers.txt
      - discussion_notes.txt
      - outcome.txt
    Returns a list of dictionaries, one per case study.
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
    return case_studies

def search_case_studies(case_studies, query):
    """
    Search through EmoPath case studies for occurrences of the query (case-insensitive)
    across all text fields (triggers, discussion_notes, outcome).
    Returns a list of matching case studies.
    """
    matching_cases = []
    query_lower = query.lower()
    for case in case_studies:
        combined_text = " ".join([
            case.get("triggers", ""),
            case.get("discussion_notes", ""),
            case.get("outcome", "")
        ]).lower()
        if query_lower in combined_text:
            matching_cases.append(case)
    return matching_cases

def build_prompt_from_cases(matching_cases, query):
    """
    Build a comprehensive prompt for the generative AI. The prompt starts by stating EmoPath’s mission,
    includes the user query, and lists the details of relevant case studies.
    """
    prompt = (
        "EmoPath Mission: Support families in raising children thoughtfully with science-based, "
        "constructive alternatives to traditional punishment. Our approach encourages interactive games, "
        "visual aids, and reflective activities that foster emotional growth and positive behavior.\n\n"
    )
    prompt += f"User Query: {query}\n\nRelevant Case Studies:\n"
    
    if not matching_cases:
        prompt += "No similar past case studies found. Please provide further details if available."
    else:
        for case in matching_cases:
            prompt += f"\nCase ID: {case['case_id']}\n"
            prompt += f"Triggers: {case.get('triggers', '')}\n"
            prompt += f"Discussion: {case.get('discussion_notes', '')}\n"
            prompt += f"Outcome: {case.get('outcome', '')}\n"
    
    prompt += (
        "\n\nBased on the above information, provide tailored, evidence-based recommendations "
        "for addressing the behavior described in the user query. Include interactive, reflective, "
        "and visual strategies where applicable."
    )
    return prompt

def generate_ai_response(prompt):
    """
    Placeholder for a generative AI model. Replace this with a call to an AI service (like OpenAI's GPT)
    to generate a tailored response based on the prompt.
    """
    # For demonstration purposes, we return a placeholder response.
    response = (
        "This is a placeholder response. In a real implementation, the AI model would generate a personalized, "
        "evidence-based recommendation based on the prompt provided."
    )
    return response

def main():
    # Define the root folder for EmoPath case studies (adjust this path as needed)
    root_folder = "./EmoPath_KnowledgeBase/Case_Studies"
    
    # Load all case studies
    case_studies = load_case_studies(root_folder)
    print(f"Loaded {len(case_studies)} case studies.\n")
    
    # Get a user query about child behavior or family challenges
    query = input("Enter your question regarding child behavior or family guidance: ")
    
    # Retrieve matching case studies based on the query
    matching_cases = search_case_studies(case_studies, query)
    print(f"\nFound {len(matching_cases)} matching case studies.\n")
    
    # Build the prompt for the generative AI
    prompt = build_prompt_from_cases(matching_cases, query)
    print("Constructed Prompt:")
    print(prompt)
    
    # Generate a response from the AI (placeholder)
    ai_response = generate_ai_response(prompt)
    print("\nAI Response:")
    print(ai_response)

if __name__ == "__main__":
    main()
