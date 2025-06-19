arg1= "```python\nimport json\nfrom urllib.request import urlopen\nfrom datetime import datetime\n\ndef get_june_2024_details():\n    # 读取JSON数据\n    with urlopen(\"http://192.168.15.83:8080/static/TraceData.json\") as response:\n        data = json.loads(response.read().decode('utf-8'))\n\n    # 初始化结果列表\n    result = []\n    \n    # 遍历数据找出2024年6月的订单\n    for order in data:\n        approve_time = order.get(\"ApproveTime\")\n        if approve_time:\n            try:\n                dt = datetime.strptime(approve_time, \"%Y-%m-%d %H:%M:%S\")\n                if dt.year == 2024 and dt.month == 6:\n                    # 复制订单数据（避免修改原数据）\n                    order_copy = order.copy()\n                    # 添加格式化后的审批时间\n                    order_copy[\"FormattedApproveTime\"] = dt.strftime(\"%Y-%m-%d %H:%M:%S\")\n                    result.append(order_copy)\n            except (ValueError, TypeError):\n                continue\n    \n    return result\n\n# 获取2024年6月的明细数据\nresult = get_june_2024_details()\n\n# 打印结果（只打印部分信息以避免过大输出）\nfor order in result[:5]:  # 只打印前5条记录作为示例\n    print({\n        \"SaleOrderNo\": order.get(\"SaleOrderNo\"),\n        \"SaleOrderType\": order.get(\"SaleOrderType\"),\n        \"ApproveTime\": order.get(\"ApproveTime\"),\n        \"SCustomerName\": order.get(\"SCustomerName\")\n    })\n\n# 打印总记录数\nprint(f\"\\n2024年6月共有 {len(result)} 条订单记录\")\n```"


def main(arg1: str) -> dict:
    import requests
    import os
    url = "http://localhost:8000/execute_and_save"
    
    payload = {
        "code": arg1,
        "filename": "test_result"  # 添加固定的测试文件名
    }
    
    # print("发送请求到:", url)
    response = requests.post(url, json=payload)
    # print("响应状态码:", response.status_code)
    # print("完整响应:", response.text)
    
    response_data = response.json()
    
    # 检查文件是否生成
    static_dir = "static"
    # json_file = os.path.join(static_dir, "test_result.json")
    # csv_file = os.path.join(static_dir, "test_result.csv")
    
    # print("\n检查文件生成:")
    # print(f"JSON文件存在: {os.path.exists(json_file)}")
    # print(f"CSV文件存在: {os.path.exists(csv_file)}")
    
    # if os.path.exists(json_file):
    #     print(f"JSON文件大小: {os.path.getsize(json_file)} 字节")
    # if os.path.exists(csv_file):
    #     print(f"CSV文件大小: {os.path.getsize(csv_file)} 字节")
    
    return {
        "result": response_data.get("output"),
        "file_url": response_data.get("file_url"),
        "csv_url": response_data.get("csv_url"),
        "status": response_data.get("status")
    }
    
if __name__ == "__main__":
    result = main(arg1)
    print("\n返回结果:")
    for key, value in result.items():
        print(f"{key}: {value}")