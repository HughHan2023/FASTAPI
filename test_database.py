import json
import urllib.request

# 下载并解析JSON数据
with urllib.request.urlopen("http://192.168.15.83:8080/static/TraceData.json") as f:
    data = json.loads(f.read().decode('utf-8'))

# 统计总订单数（Apheresis和Transfusion记录总数之和）
total_orders = 0

for order in data:
    apheresis_list = order.get('Apheresis', [])
    transfusion_list = order.get('Transfusion', [])
    
    total_orders += len(apheresis_list) + len(transfusion_list)

# 输出结果
print(f"4-6月订单总数: {total_orders}")
