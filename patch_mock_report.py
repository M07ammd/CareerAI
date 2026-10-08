import re

# Fix test_graph.py
f = "tests/test_graph.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'hiring_probability="Medium",',
    'hiring_probability="Medium",\n                    top_recommendations="| Finding | Evidence |",',
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix test_api.py (if ReportSummary mock exists)
f = "tests/test_api.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'ReportSummary\(\s*executive_summary="Excellent",\s*score_interpretation="Great",\s*hiring_probability="High"\s*\)',
    'ReportSummary(executive_summary="Excellent", score_interpretation="Great", hiring_probability="High", top_recommendations="| Finding | Evidence |")',
    c
)
open(f, "w", encoding="utf-8").write(c)
print("ReportSummary mocks patched")
