import requests
import json
from datetime import datetime
import pandas as pd

# 1. 下载数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = requests.get(url)
response.encoding = 'utf-8'
data = response.json()

# 2. 过滤2025年5月的择期订单
result_rows = []
for order in data:
    # 订单类型为择期订单
    if order.get("SaleOrderType") != "择期订单":
        continue
    # 订单日期为2025年5月
    sale_order_date = order.get("SaleOrderDate")
    if not sale_order_date:
        continue
    try:
        dt = datetime.strptime(sale_order_date, "%Y-%m-%d")
    except Exception:
        continue
    if dt.year != 2025 or dt.month != 5:
        continue

    # 平铺明细，去除嵌套
    row = {
        "销售订单ID": order.get("sale_order_id"),
        "销售订单编号": order.get("SaleOrderNo"),
        "订单日期": order.get("SaleOrderDate"),
        "客户编号": order.get("SCustomerNo"),
        "客户姓名": order.get("SCustomerName"),
        "客户姓名缩写": order.get("SCustomerNameSX"),
        "订单类型": order.get("SaleOrderType"),
        "是否已关闭": order.get("is_closed"),
        "审批时间": order.get("ApproveTime"),
        "生产通知时间": order.get("NoticeProduceTime"),
        "确认日期": order.get("ConfirmDate"),
        "医院ID": order.get("HostipalID"),
    }
    result_rows.append(row)

# 3. 结果存入result变量
result = result_rows

# 4. 打印结果
print(result)