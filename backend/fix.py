with open('agents/orchestrator_agent.py', 'r') as f:
    content = f.read()

# remove old bad sys.path lines:
lines = content.split('\n')
new_lines = []
for line in lines:
    if 'sys.path.insert(0,' in line or 'backend_dir =' in line or '# Append sub-agent' in line:
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)
import_block = """import os
import sys

# Append sub-agent dirs so absolute inner imports work
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(backend_dir, "agents", "sponsor_agent"))
sys.path.insert(0, os.path.join(backend_dir, "agents", "pricing_agent"))
sys.path.insert(0, os.path.join(backend_dir, "agents", "exhibitor_agent"))
sys.path.insert(0, os.path.join(backend_dir, "agents", "community_agent"))
sys.path.insert(0, os.path.join(backend_dir, "agents", "instagram_agent"))
"""
content = content.replace("import os\nimport sys", import_block, 1)
with open('agents/orchestrator_agent.py', 'w') as f:
    f.write(content)
