import requests
import json
import pandas as pd

# 1. 下载数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = requests.get(url)
response.encoding = 'utf-8'
data = response.json()

# 2. 提取生产中的明细数据
# 生产中定义：生产工艺（TechniqueStandardName）不为'PBMC分离冻存'，且生产批次状态（ProdBatchStatus）为'生产中'
rows = []
for order in data:
    sale_order_no = order.get("SaleOrderNo")
    sale_order_date = order.get("SaleOrderDate")
    sale_order_type = order.get("SaleOrderType")
    hospital_id = order.get("HostipalID")
    customer_no = order.get("SCustomerNo")
    is_closed = order.get("is_closed")
    confirm_date = order.get("ConfirmDate")
    approve_time = order.get("ApproveTime")
    # 遍历单采
    for aph in order.get("Apheresis", []):
        dan_cai_no = aph.get("DanCaiNo")
        coi_no = aph.get("CoiNo")
        apheresis_date = aph.get("apheresis_date")
        apheresis_end = aph.get("apheresis_end")
        batch_no = aph.get("BatchNo")
        # 遍历生产批次
        for pb in aph.get("ProdBatch", []):
            # 过滤条件
            if pb.get("TechniqueStandardName") != "PBMC分离冻存" and pb.get("ProdBatchStatus") == "生产中":
                row = {
                    "销售订单编号": sale_order_no,
                    "订单日期": sale_order_date,
                    "订单类型": sale_order_type,
                    "医院ID": hospital_id,
                    "客户编号": customer_no,
                    "是否已关闭": is_closed,
                    "订单确认日期": confirm_date,
                    "订单批准时间": approve_time,
                    "单采编号": dan_cai_no,
                    "COI编号": coi_no,
                    "单采日期": apheresis_date,
                    "单采结束时间": apheresis_end,
                    "批次号": batch_no,
                    "生产批次ID": pb.get("ProdBatchID"),
                    "生产批次编码": pb.get("ProdBatchCode"),
                    "车间名称": pb.get("WorkshopName"),
                    "技术标准名称": pb.get("TechniqueStandardName"),
                    "生产批次状态": pb.get("ProdBatchStatus"),
                    "审核日期": pb.get("AuditDate"),
                    "工序名称": pb.get("ProcName"),
                    "工作开始时间": pb.get("WorkStartTime"),
                    "工作结束时间": pb.get("WorkEndTime"),
                }
                # 产品信息（平铺）
                product = pb.get("Product", {})
                row["COA编号Q"] = product.get("COANoQ")
                row["COA编号"] = product.get("COANo")
                row["制药快速放行"] = product.get("制药快速放行")
                row["制药快速放行日期"] = product.get("制药快速放行日期")
                row["制药快速放行操作时间"] = product.get("制药快速放行操作时间")
                row["MAH快速放行"] = product.get("MAH快速放行")
                row["质量状态"] = product.get("QualityStatus")
                # 生产详情（平铺）
                detail = pb.get("Detail", {})
                row["生产详情_工序名称"] = detail.get("ProcName")
                row["生产详情_工作开始时间"] = detail.get("WorkStartTime")
                row["生产详情_工作结束时间"] = detail.get("WorkEndTime")
                rows.append(row)

# 3. 结果存入result变量
result = rows

# 4. 打印结果
print(result)