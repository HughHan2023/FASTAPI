import json
import urllib.request
from datetime import datetime

# 下载并解析JSON数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = urllib.request.urlopen(url)
data_str = response.read().decode("utf-8")
orders = json.loads(data_str)

# 初始化统计计数器
count = 0

# 遍历每个订单记录
for order in orders:
    # 提取订单日期和审批时间字段
    sale_date_str = order.get("SaleOrderDate")
    approve_time_str = order.get("ApproveTime")

    # 跳过缺少订单日期或审批时间的记录
    if sale_date_str is None or approve_time_str is None:
        continue

    try:
        # 解析订单日期
        sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d")
    except ValueError:
        # 跳过日期格式不正确的记录
        continue

    # 判断是否为2025年4月的订单
    if sale_date.year == 2025 and sale_date.month == 4:
        count += 1

# 输出结果
result = count
print(result)