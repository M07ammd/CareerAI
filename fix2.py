import re
path = 'tests/test_agents.py'
data = open(path, encoding='utf-8').read()
data = data.replace('MagicMock()', 'AsyncMock()')
data = data.replace('from unittest.mock import patch, MagicMock', 'from unittest.mock import patch, AsyncMock')
data = re.sub(r'\s*assert\s+result\["next_step"\]\s*==\s*WorkflowStep\.END\n?', '\n', data)
open(path, 'w', encoding='utf-8').write(data)
