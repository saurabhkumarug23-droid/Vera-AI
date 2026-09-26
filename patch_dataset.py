with open("dataset/generate_dataset.py", "r") as f:
    code = f.read()

code = code.replace('default="."', 'default="dataset"')

with open("dataset/generate_dataset.py", "w") as f:
    f.write(code)
