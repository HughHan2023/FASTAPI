import urllib.request
import json
from datetime import datetime

# 下载并读取JSON数据
url = "http://192.168.15.83:8080/static/TraceData.json"
with urllib.request.urlopen(url) as response:
    data = response.read().decode('utf-8')
    orders = json.loads(data)

# 目标时间段
start_month = datetime(2025, 2, 1)
end_month = datetime(2025, 5, 31)

# 统计每个月的订单数量
from collections import defaultdict

monthly_counts = defaultdict(set)  # 用set去重订单号

for order in orders:
    sale_order_date_str = order.get("SaleOrderDate")
    sale_order_no = order.get("SaleOrderNo")
    if not sale_order_date_str or not sale_order_no:
        continue
    try:
        sale_order_date = datetime.strptime(sale_order_date_str, "%Y-%m-%d")
    except Exception:
        continue
    if start_month <= sale_order_date <= end_month:
        month_key = sale_order_date.strftime("%Y-%m")
        monthly_counts[month_key].add(sale_order_no)

# 构造结果
result = []
for year in [2025]:
    for month in range(2, 6):
        month_key = f"{year}-{month:02d}"
        count = len(monthly_counts.get(month_key, set()))
        result.append({"month": month_key, "order_count": count})

print(result)