import re

# Fix test_graph.py
f = "tests/test_graph.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'explanation="Good match\.",',
    'explanation="Good match.",\n                    strengths="| Finding | Evidence |",',
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix test_api.py
f = "tests/test_api.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'explanation="Excellent fit\."',
    'explanation="Excellent fit.",\n                strengths="| Finding | Evidence |"',
    c
)
c = re.sub(
    r'hiring_probability="High",\s*full_report_markdown=".*?",',
    'hiring_probability="High",\n            top_recommendations="| Finding | Evidence |",\n            full_report_markdown="# Report",',
    c
)
open(f, "w", encoding="utf-8").write(c)
print("tests patched again double quotes")
