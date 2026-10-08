import re

# Fix test_graph.py
f = "tests/test_graph.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r"explanation='Good match\.',",
    "explanation='Good match.',\n                strengths='| Finding | Evidence |',",
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix test_api.py
f = "tests/test_api.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r"explanation='Excellent fit\.'",
    "explanation='Excellent fit.',\n                strengths='| Finding | Evidence |'",
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix test_schemas.py WorkflowStep count
f = "tests/test_schemas.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r"assert len\(steps\) == 8  # 7 agents \+ END",
    "assert len(steps) == 9  # 8 agents + END",
    c
)
open(f, "w", encoding="utf-8").write(c)
print("tests patched again")
