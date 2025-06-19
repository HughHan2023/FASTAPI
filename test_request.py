def main(arg1: str) -> dict:
    import urllib.request
    import urllib.error
    import json
    import time
    from urllib.parse import urlparse

    url = "http://192.168.15.83:5000/execute"
    
    # 处理输入参数，确保是有效的字符串
    try:
        if isinstance(arg1, str):
            # 如果输入是字符串形式的JSON，尝试解析它
            if arg1.strip().startswith('{'):
                arg1 = json.loads(arg1).get('arg1', arg1)
        payload = {
            "code": arg1
        }
    except json.JSONDecodeError:
        payload = {
            "code": arg1
        }

    # 准备请求
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(data))
    }

    # 创建请求对象
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    # 最大重试次数
    max_retries = 3
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            # 发送请求
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                
                if response_data.get("status") == "error":
                    return {
                        "error_message": response_data.get("error", "Unknown error"),
                        "error_type": "CodeNodeError"
                    }
                
                # 尝试解析输出为JSON
                output = response_data.get("output", "")
                try:
                    # 如果输出是JSON字符串，解析它
                    if output.strip().startswith('{'):
                        result = json.loads(output)
                        return {"result": result}
                except json.JSONDecodeError:
                    pass  # 如果不是JSON，直接返回原始输出
                
                return {
                    "result": output
                }

        except urllib.error.URLError as e:
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2)  # 等待2秒后重试
            continue
        except json.JSONDecodeError as e:
            return {
                "error_message": f"JSON parsing error: {str(e)}",
                "error_type": "CodeNodeError"
            }
        except Exception as e:
            return {
                "error_message": f"Unexpected error: {str(e)}",
                "error_type": "CodeNodeError"
            }

    # 如果所有重试都失败了
    return {
        "error_message": f"Request failed after {max_retries} retries: {str(last_error)}",
        "error_type": "CodeNodeError"
    }