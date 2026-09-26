import re
import os

with open("judge_simulator.py", "r") as f:
    code = f.read()

if "import os" not in code:
    code = "import os\n" + code

code = re.sub(
    r'LLM_API_KEY = "sk-.*?"', 
    'LLM_API_KEY = os.getenv("LLM_API_KEY", "")', 
    code
)
code = re.sub(
    r'LLM_API_KEY = ".*?"', 
    'LLM_API_KEY = os.getenv("LLM_API_KEY", "")', 
    code
)

with open("judge_simulator.py", "w") as f:
    f.write(code)

with open(".env.example", "w") as f:
    f.write('LLM_API_KEY="your_api_key_here"\nLLM_PROVIDER="openai"\nLLM_MODEL="gpt-4o-mini"\n')
