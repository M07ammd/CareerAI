import os
import re

for root, _, files in os.walk('c:/Users/moham/OneDrive/Desktop/CareerAI/tests'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('from backend', 'from app')
            content = content.replace('import backend', 'import app')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
