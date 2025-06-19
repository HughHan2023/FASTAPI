import urllib.request
import json
from datetime import datetime

# 定义辅助函数，安全解析日期
def parse_datetime(dt_str):
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(dt_str, fmt)
        except Exception:
            continue
    return None

# 目标时间范围
target_year = 2025
target_month = 3

# 下载数据
url = "http://192.168.15.83:8080/static/TraceData.json"
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode('utf-8'))

投产订单明细 = []

for order in data:
    订单编号 = order.get("SaleOrderNo")
    订单类型 = order.get("SaleOrderType")
    客户姓名 = order.get("SCustomerName")
    订单日期 = order.get("SaleOrderDate")
    医院ID = order.get("HostipalID")
    单采列表 = order.get("Apheresis", [])
    # 投产订单明细：遍历所有生产批次
    for apheresis in 单采列表:
        prod_batch_list = apheresis.get("ProdBatch", [])
        for prod in prod_batch_list:
            # 生产工艺
            技术标准 = prod.get("TechniqueStandardName")
            # 生产批次编码
            生产批次编码 = prod.get("ProdBatchCode")
            # 生产批次状态
            生产批次状态 = prod.get("ProdBatchStatus")
            # 生产工序
            工序名称 = prod.get("ProcName")
            # 生产开始时间
            生产开始时间 = prod.get("WorkStartTime")
            dt_生产开始 = parse_datetime(生产开始时间)
            # 只统计2025年3月的投产订单
            if dt_生产开始 and dt_生产开始.year == target_year and dt_生产开始.month == target_month:
                投产订单明细.append({
                    "订单编号": 订单编号,
                    "订单类型": 订单类型,
                    "客户姓名": 客户姓名,
                    "订单日期": 订单日期,
                    "医院ID": 医院ID,
                    "单采编号": apheresis.get("DanCaiNo"),
                    "COI编号": apheresis.get("CoiNo"),
                    "生产批次编码": 生产批次编码,
                    "生产工艺": 技术标准,
                    "生产批次状态": 生产批次状态,
                    "工序名称": 工序名称,
                    "生产开始时间": 生产开始时间
                })

result = 投产订单明细

# 打印结果
for row in result:
    print(row)