import requests
import json
import pandas as pd

# 1. 下载数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = requests.get(url)
response.encoding = 'utf-8'
data = response.json()

# 2. 明细数据平铺
records = []
for order in data:
    sale_order_no = order.get("SaleOrderNo")
    sale_order_date = order.get("SaleOrderDate")
    order_type = order.get("SaleOrderType")
    hospital_id = order.get("HostipalID")
    customer_no = order.get("SCustomerNo")
    is_closed = order.get("is_closed")
    approve_time = order.get("ApproveTime")
    confirm_date = order.get("ConfirmDate")
    # 生产批次明细平铺
    if order.get("Apheresis"):
        for aph in order["Apheresis"]:
            dan_cai_no = aph.get("DanCaiNo")
            apheresis_date = aph.get("apheresis_date")
            apheresis_end = aph.get("apheresis_end")
            batch_no = aph.get("BatchNo")
            if aph.get("ProdBatch"):
                for pb in aph["ProdBatch"]:
                    prod_batch_code = pb.get("ProdBatchCode")
                    technique_standard_name = pb.get("TechniqueStandardName")
                    prod_batch_status = pb.get("ProdBatchStatus")
                    work_start_time = pb.get("WorkStartTime")
                    work_end_time = pb.get("WorkEndTime")
                    # 生产中的订单定义：生产工艺不为'PBMC分离冻存'，且WorkStartTime不为空，且WorkEndTime为空，且生产批次状态不是'生产终止'
                    if (
                        technique_standard_name != "PBMC分离冻存"
                        and work_start_time
                        and not work_end_time
                        and prod_batch_status != "生产终止"
                    ):
                        records.append({
                            "销售订单编号": sale_order_no,
                            "订单日期": sale_order_date,
                            "订单类型": order_type,
                            "医院ID": hospital_id,
                            "客户编号": customer_no,
                            "是否已关闭": is_closed,
                            "审批时间": approve_time,
                            "确认日期": confirm_date,
                            "单采编号": dan_cai_no,
                            "单采日期": apheresis_date,
                            "单采结束时间": apheresis_end,
                            "批次号": batch_no,
                            "生产批次编码": prod_batch_code,
                            "生产工艺": technique_standard_name,
                            "生产批次状态": prod_batch_status,
                            "生产开始时间": work_start_time,
                            "生产结束时间": work_end_time
                        })

# 3. 结果存入result变量
result = records

# 4. 打印结果
print(result)