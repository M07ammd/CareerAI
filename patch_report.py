import re

# Fix models.py
f = "app/schemas/models.py"
c = open(f, "r", encoding="utf-8").read()
c = re.sub(
    r'key_strengths: List\[str\] = Field\(default_factory=list\)',
    'key_strengths: str = Field(default="")',
    c
)
open(f, "w", encoding="utf-8").write(c)

# Fix report_agent.py
f = "app/agents/report_agent.py"
c = open(f, "r", encoding="utf-8").read()
# Add top_recommendations to ReportSummary
c = re.sub(
    r'hiring_probability: str = Field\(description="Estimated likelihood of success: Low / Medium / High"\)',
    'hiring_probability: str = Field(description="Estimated likelihood of success: Low / Medium / High")\n    top_recommendations: str = Field(description="MUST be a Markdown table with exactly two columns: \'Finding\' and \'Evidence from CV\'.")',
    c
)
# Add to SYSTEM_PROMPT
c = re.sub(
    r'"4\. CV Bullet Rewrites \(2-3 suggestions improving existing bullet points\)\\n"',
    '"4. CV Bullet Rewrites (2-3 suggestions improving existing bullet points)\\n"\n    "5. Top Recommendations as a Markdown table with columns: Finding, Evidence from CV\\n"',
    c
)

# Fix assignment
c = re.sub(
    r'key_strengths = sm\.strengths if sm else \[\]',
    'key_strengths = sm.strengths if sm else ""',
    c
)
c = re.sub(
    r'top_recs = \[\]\n\s*if cr:\n\s*top_recs = \[a\.title for a in cr\.immediate_actions\] \+ \[a\.title for a in cr\.short_term_goals\]\n\s*top_recs = top_recs\[:5\]',
    'top_recs = summary_result.top_recommendations',
    c
)

open(f, "w", encoding="utf-8").write(c)
print("models and report_agent patched")
