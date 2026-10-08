import re

f = "app/api/routes.py"
content = open(f, "r", encoding="utf-8").read()
# Remove Depends(_check_api_key) lines
content = re.sub(r'^\s*_auth:\s*None\s*=\s*Depends\(_check_api_key\),\n?', '', content, flags=re.MULTILINE)

# Also ensure it is removed from the import if it exists
content = re.sub(r'from app\.api\.dependencies import _check_api_key,\s*limiter', 'from app.api.dependencies import limiter', content)

open(f, "w", encoding="utf-8").write(content)
print("routes.py cleaned up")
