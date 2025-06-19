import urllib.request
import json
import datetime

# 数据文件URL
data_url = "http://192.168.15.83:8080/static/TraceData.json"

# 下载并解析JSON数据
with urllib.request.urlopen(data_url) as response:
    data = json.loads(response.read().decode('utf-8'))

count = 0

# 遍历每个订单检查日期
for order in data:
    date_str = order.get('SaleOrderDate')
    if date_str:
        try:
            # 将字符串转换为日期对象
            order_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            # 检查是否为2025年4月
            if order_date.year == 2025 and order_date.month == 4:
                count += 1
        except ValueError:
            # 忽略格式错误的日期
            continue

result = count
print(f"2025年4月的订单数量为: {result}")