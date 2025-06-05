import re
arg1=  

def main(arg1: str) -> dict:
    matches = re.findall(r"```python(.*?)```", arg1, re.DOTALL)
    raw_code = matches[0].strip()
    print(raw_code)
if __name__ == "__main__":
    main(arg1)