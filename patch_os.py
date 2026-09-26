with open("judge_simulator.py", "r") as f:
    code = f.read()

if "import os" not in code:
    code = "import os\n" + code

with open("judge_simulator.py", "w") as f:
    f.write(code)
