import test_request
import json

test_input = {
    "arg1": """```python
import json
import urllib.request
from datetime import datetime

# 下载并加载JSON数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))

# 初始化结果字典
result = {
    "2024年5月订单数": 0,
    "2024年5月单采数": 0,
    "2024年5月已输注订单数": 0
}

# 检查订单是否在2024年5月
for order in data:
    try:
        # 使用ApproveTime作为订单生效时间
        if order.get("ApproveTime"):
            approve_time = datetime.strptime(order["ApproveTime"], "%Y-%m-%d %H:%M:%S")
            if approve_time.year == 2024 and approve_time.month == 5:
                result["2024年5月订单数"] += 1
                
                # 检查单采记录
                if "Apheresis" in order and order["Apheresis"]:
                    for apheresis in order["Apheresis"]:
                        if apheresis.get("apheresis_end"):
                            apheresis_time = datetime.strptime(apheresis["apheresis_end"], "%Y-%m-%d %H:%M:%S")
                            if apheresis_time.year == 2024 and apheresis_time.month == 5:
                                result["2024年5月单采数"] += 1
                
                # 检查输注记录
                if "Transfusion" in order and order["Transfusion"]:
                    for transfusion in order["Transfusion"]:
                        if transfusion.get("actual_transfusion_time"):
                            transfusion_time = datetime.strptime(transfusion["actual_transfusion_time"], "%Y-%m-%d %H:%M:%S")
                            if transfusion_time.year == 2024 and transfusion_time.month == 5:
                                result["2024年5月已输注订单数"] += 1
    except Exception as e:
        # 忽略数据处理中的错误
        continue

# 打印结果
print(result)
```"""
}

if __name__ == "__main__":
    print("开始测试...")
    result = test_request.main(json.dumps(test_input))
    print("\n测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 