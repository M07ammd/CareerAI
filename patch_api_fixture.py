import re

# Fix test_api.py (fake_analysis_response)
f = "tests/test_api.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'explanation="Good match\.",\s*\),',
    'explanation="Good match.",\n            strengths="| Finding | Evidence |",\n        ),',
    c
)
c = re.sub(
    r'hiring_probability="Medium",\s*full_report_markdown="# Report\\n\\nGood match\.",',
    'hiring_probability="Medium",\n            top_recommendations="| Finding | Evidence |",\n            full_report_markdown="# Report\\n\\nGood match.",',
    c
)
open(f, "w", encoding="utf-8").write(c)
print("test_api.py fixture patched")
