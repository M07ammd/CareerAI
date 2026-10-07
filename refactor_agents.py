import os
import re

agent_files = [
    'resume_agent.py', 'job_agent.py', 'skill_agent.py',
    'gap_agent.py', 'interview_agent.py', 'roadmap_agent.py', 'report_agent.py'
]

for filename in agent_files:
    path = os.path.join('app', 'agents', filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. async def
    content = re.sub(r'def (\w+_agent)\(state: CareerPilotState\) -> dict:', r'async def \1(state: CareerPilotState) -> dict:', content)
    
    # 2. await llm.ainvoke / chain.ainvoke
    content = content.replace('.invoke(messages)', '.ainvoke(messages)')
    content = content.replace('llm.invoke', 'await llm.ainvoke')
    content = content.replace('chain.invoke', 'await chain.ainvoke')
    
    # 3. Add await before get_structured_llm if it was missed... wait, get_structured_llm is synchronous (returns an object).
    # so we just need await before .ainvoke
    content = re.sub(r'(result[^=]*=\s*)([a-zA-Z0-9_]+)\.ainvoke', r'\1await \2.ainvoke', content)

    # 4. Remove next_step and retry_count lines from returns
    content = re.sub(r'\s*"next_step": WorkflowStep\.[A-Z_]+,\n?', '', content)
    content = re.sub(r'\s*"retry_count": [^,]+,\n?', '', content)

    # 5. Add prompt injection utils
    if 'prompt_utils' not in content:
        content = content.replace('from app.schemas.models', 'from app.agents.prompt_utils import wrap_user_content, ANTI_INJECTION_INSTRUCTION\nfrom app.schemas.models')

    # 6. Apply prompt injection
    if '---RESUME START---' in content:
        content = re.sub(
            r'f?"Please analyze the following .*\\n\\n"[\s\S]*?"---RESUME START---\\n\{resume_text\}\\n---RESUME END---"',
            r'f"Please analyze the following resume and extract all structured information:\n\n{wrap_user_content(\'RESUME\', resume_text)}"',
            content
        )
    if '---JOB DESCRIPTION START---' in content:
        content = re.sub(
            r'f?"Please analyze the following .*\\n\\n"[\s\S]*?"---JOB DESCRIPTION START---\\n\{job_description\}\\n---JOB DESCRIPTION END---"',
            r'f"Please analyze the following job description and extract all structured information:\n\n{wrap_user_content(\'JOB DESCRIPTION\', job_description)}"',
            content
        )
    if 'ANTI_INJECTION_INSTRUCTION' not in content and 'SYSTEM_PROMPT = """' in content:
        content = content.replace('SYSTEM_PROMPT = """', 'SYSTEM_PROMPT = """\n{ANTI_INJECTION_INSTRUCTION}\n')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

