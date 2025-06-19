from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import re
from io import StringIO
import contextlib
import os
import json
import time
from datetime import datetime
import random
import string
import pandas as pd
from urllib.request import urlopen

app = FastAPI()

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 确保static目录存在
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# 挂载静态文件目录，设置目录列表为True以允许浏览
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

class CodeRequest(BaseModel):
    code: str

class SaveRequest(BaseModel):
    code: str
    filename: str = None  # 可选的文件名参数

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

@app.post("/execute_and_save")
async def execute_and_save(request: SaveRequest):
    try:
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        filename = f"result_{timestamp}_{random_str}.json"
        
        # 执行代码并捕获输出
        with capture_output() as (stdout, stderr):
            # 处理代码字符串
            code_to_execute = request.code
            if code_to_execute.startswith("```python"):
                # 提取代码块内容
                code_blocks = re.findall(r"```python\n(.*?)```", code_to_execute, re.DOTALL)
                if code_blocks:
                    code_to_execute = code_blocks[0]
            
            # 清理代码字符串
            code_to_execute = code_to_execute.strip()
            
            # 创建执行环境
            exec_globals = {
                'json': json,
                'urlopen': urlopen,
                'datetime': datetime,
                'pd': pd,
                '__builtins__': __builtins__
            }
            local_vars = {}
            
            # 执行代码
            exec(code_to_execute, exec_globals, local_vars)
            
            # 获取输出
            output = stdout.getvalue()
            error = stderr.getvalue()
            
            # 从本地变量中获取结果数据
            # 尝试从output中获取结果，如果output为空则从local_vars获取
            result_data = []
            if output:
                try:
                    # 尝试将output解析为JSON
                    result_data = json.loads(output)
                except json.JSONDecodeError:
                    # 如果output不是JSON格式，则从local_vars获取
                    result_data = local_vars.get('result', [])
            else:
                result_data = local_vars.get('result', [])
            if not result_data:
                raise ValueError("代码执行结果为空，请确保代码中定义了 'result' 变量")
            
            # 确保static目录存在
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)
            
            # 保存结果到JSON文件
            file_path = os.path.join(static_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            # 将数据转换为DataFrame并保存为CSV

            #df = pd.DataFrame(result_data)
            df=pd.json_normalize(result_data)
            csv_filename = os.path.splitext(filename)[0] + '.csv'
            csv_path = os.path.join(static_dir, csv_filename)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            return {
                "status": "success",
                "file_url": f"/static/{filename}",
                "csv_url": f"/static/{csv_filename}",
                "message": "数据已保存为JSON和CSV文件"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "执行或保存过程中发生错误"
        }

