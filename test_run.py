import urllib.request
import json
from datetime import datetime

# 下载并读取JSON数据
url = "http://192.168.15.83:8080/static/TraceData.json"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode('utf-8'))

# 目标时间段
start_month = datetime(2025, 2, 1)
end_month = datetime(2025, 5, 31)

# 统计每个月的订单数量
from collections import OrderedDict

# 初始化每月计数
months = OrderedDict()
for m in range(2, 6):
    key = f"2025-{m:02d}"
    months[key] = 0

for order in data:
    sale_order_date_str = order.get("SaleOrderDate")
    if not sale_order_date_str:
        continue
    try:
        sale_order_date = datetime.strptime(sale_order_date_str, "%Y-%m-%d")
    except Exception:
        continue
    if start_month <= sale_order_date <= end_month:
        month_key = sale_order_date.strftime("%Y-%m")
        if month_key in months:
            months[month_key] += 1

result = dict(months)
print(result)