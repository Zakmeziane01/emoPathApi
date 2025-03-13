
import os

def create_file(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created file: {filepath}")

# Define the base folder for the knowledge base
knowledge_base_dir = "knowledge-base"
subfolders = ["case_studies", "guidelines", "resources", "other"]

# Create the folder structure
for folder in subfolders:
    os.makedirs(os.path.join(knowledge_base_dir, folder), exist_ok=True)

# ===================== Case Study 1 =====================

case_study_1 = """# Case Study: Managing Homework Resistance

**Child's Age:** 8 years  
**Behavior:** Refusing to complete homework, arguing with parents  

## Background  
The child began resisting homework assignments after transitioning to a new school. He would often cry, complain of stomach aches, and refuse to sit down to work. 

## Parent’s Initial Response  
- Encouraged the child to "try harder"  
- Removed playtime as a consequence for unfinished homework  

## Recommended Approach  
1. **Reduce Pressure:** Create a predictable homework schedule with 10-minute work blocks followed by 5-minute breaks.  
2. **Positive Reinforcement:** Reward effort, not just completion. Praise the child for sitting down and trying.  
3. **Emotional Check-In:** Before starting, ask how the child is feeling. If they express anxiety, try deep breathing exercises or a short walk.  

## Outcome  
After implementing these changes, the child's resistance decreased. He began completing assignments with fewer complaints, and his anxiety levels reduced.  
"""

create_file(os.path.join(knowledge_base_dir, "case_studies"), "Case_001.md", case_study_1)

# ===================== Case Study 2 =====================

case_study_2 = """# Case Study: Aggression Toward Siblings

**Child's Age:** 6 years  
**Behavior:** Hitting younger sibling during play  

## Background  
The child displayed increased aggression after the arrival of a new sibling. The child would hit, push, and scream when the younger sibling received attention from parents.  

## Parent’s Initial Response  
- Told the child to "stop being mean"  
- Sent the child to time-out  

## Recommended Approach  
1. **Acknowledge Feelings:** "I can see you’re upset because your brother got more attention. It’s okay to feel upset."  
2. **Teach Alternative Behavior:** Suggest using words like "I feel left out" instead of hitting.  
3. **Reinforce Positive Interaction:** Encourage cooperative play and praise positive sibling interactions.  

## Outcome  
The child's aggressive behavior decreased by 60% over three weeks. Positive sibling interactions increased, and the child began verbalizing emotions instead of acting out physically.  
"""

create_file(os.path.join(knowledge_base_dir, "case_studies"), "Case_002.md", case_study_2)

# ===================== Guidelines =====================

guidelines_content = """# Guidelines for Positive Discipline

## Key Principles
1. **Consistency:** Parents should respond to behavior consistently to avoid confusion.  
2. **Empathy First:** Before correcting behavior, acknowledge the child’s emotional state.  
3. **Positive Reinforcement:** Reward the behavior you want to see more of.  
4. **Avoid Harsh Punishment:** Research shows that punitive measures increase aggression and anxiety.  

## When Facing Challenging Behavior:
✅ Stay calm and maintain a neutral tone.  
✅ Describe the problem behavior without judgment.  
✅ Ask the child to express their feelings using words.  
✅ Offer the child two choices for resolution to give them a sense of control.  

## Example:  
Instead of saying, *"Stop throwing your toys!"*  
➡️ Say: *"I see you’re upset. Would you like to calm down by reading a book or drawing?"*  
"""

create_file(os.path.join(knowledge_base_dir, "guidelines"), "Guideline_001.md", guidelines_content)

# ===================== Resources =====================

resources_content = """# Research Resource: Emotional Regulation in Children

**Author:** Dr. Jane Reynolds, Child Psychologist  
**Summary:**  
This study highlights how children between the ages of 5–10 develop emotional regulation skills. Research confirms that positive reinforcement and collaborative problem-solving increase emotional resilience by up to 45% over punitive methods.  

**Key Findings:**  
- Children are more likely to adopt positive behaviors when they feel emotionally supported.  
- Punitive consequences like time-outs and grounding can increase long-term anxiety.  
- Parental modeling of emotional control leads to improved emotional regulation in children.  

**Suggested Reading:**  
1. Dr. Ross Greene - *The Explosive Child*  
2. Daniel Siegel - *The Whole-Brain Child*  
"""

create_file(os.path.join(knowledge_base_dir, "resources"), "Resource_001.md", resources_content)

# ===================== About =====================

about_content = """# About EmoPath Knowledge Base

**Mission:**  
EmoPath supports parents in raising emotionally healthy children using science-based strategies. We focus on providing alternatives to punitive discipline, helping parents understand behavior patterns and respond with empathy and structure.  

**How It Works:**  
1. Track your child’s behavior using our built-in logging system.  
2. Receive tailored recommendations based on behavior patterns.  
3. Implement strategies and provide feedback on outcomes.  
4. Adjust strategies based on ongoing insights from the platform.  

Our goal is to empower parents with tools to navigate emotional challenges with understanding and clarity.  
"""

create_file(os.path.join(knowledge_base_dir, "other"), "About.md", about_content)
