from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import re
from io import StringIO
import contextlib
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class CodeRequest(BaseModel):
    code: str

@contextlib.contextmanager
def capture_output():
    """Capture stdout and stderr"""
    stdout, stderr = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        yield stdout, stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

@app.post("/execute")
async def execute_code(request: CodeRequest):
    try:     
        with capture_output() as (stdout, stderr):   
            matches = re.findall(r"```python(.*?)```", request.code, re.DOTALL)
            print(matches)
            if matches[0]=="":
                matches[0]=request.code
                matches[0]=matches[0].strip()
            exec(matches[0])
        return {
            "output": stdout.getvalue(),
            "error": stderr.getvalue(),
            "status": "success"
        }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "status": "error"
        }

@app.get("/tracedata")
async def get_trace_data():
    return {"url": "/static/TraceData.json"}

