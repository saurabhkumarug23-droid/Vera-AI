import re

with open("judge_simulator.py", "r") as f:
    code = f.read()

# 1. Remove HeuristicProvider
code = re.sub(r'class HeuristicProvider.*?class OpenRouterProvider', 'class OpenRouterProvider', code, flags=re.DOTALL)
# 2. Revert LLM_PROVIDER
code = re.sub(r'LLM_PROVIDER = "heuristic"', 'LLM_PROVIDER = "openai"', code)
# 3. Remove heuristic from providers map
code = re.sub(r'"heuristic": lambda: HeuristicProvider\(LLM_API_KEY, LLM_MODEL\),?', '', code)
# 4. Remove ssl verify disable if present
code = re.sub(r'import ssl\nssl\._create_default_https_context = ssl\._create_unverified_context\n*', '', code)
# 5. Fix dates back to datetime.utcnow().isoformat() + "Z"
code = code.replace('"2026-04-20T12:00:00Z"', 'datetime.utcnow().isoformat() + "Z"')

with open("judge_simulator.py", "w") as f:
    f.write(code)
