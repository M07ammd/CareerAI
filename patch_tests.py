import re

# Fix test_agents.py
f = "tests/test_agents.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'missing_skills=\["LangGraph"\],\s*match_score=72\.0,\s*explanation="Good match overall\.",',
    'missing_skills=["LangGraph"],\n            match_score=72.0,\n            explanation="Good match overall.",\n            strengths="| Finding | Evidence |",',
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix test_schemas.py
f = "tests/test_schemas.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'match_score=75,\s*explanation="Good match overall\.",',
    'match_score=75,\n            explanation="Good match overall.",\n            strengths="| Finding | Evidence |",',
    c
)
c = re.sub(
    r'partially_matched_skills=\[\s*SkillMatchDetail\(\s*skill="Kubernetes",\s*level=MatchLevel\.PARTIAL,\s*notes="Has Docker experience",\s*\)\s*\],',
    'strengths="| Finding | Evidence |",\n            partially_matched_skills=[\n                SkillMatchDetail(\n                    skill="Kubernetes",\n                    level=MatchLevel.PARTIAL,\n                    notes="Has Docker experience",\n                )\n            ],',
    c
)
c = re.sub(
    r'hiring_probability="High",\s*full_report_markdown="# Report\\n\\nDetails here\.\.\.",',
    'hiring_probability="High",\n        full_report_markdown="# Report\\n\\nDetails here...",\n        top_recommendations="| Finding | Evidence |",',
    c
)
open(f, "w", encoding="utf-8").write(c)
print("tests patched")
