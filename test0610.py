import requests
import json

# 1. 获取数据
url = "http://192.168.15.83:8080/static/TraceData.json"
response = requests.get(url)
response.encoding = 'utf-8'
data = response.json()

# 2. 查询患者000018的订单状态
result = []
for order in data:
    if order.get("SCustomerNo") == "000018":
        # 订单基本信息
        row = {
            "销售订单编号": order.get("SaleOrderNo"),
            "订单日期": order.get("SaleOrderDate"),
            "订单类型": order.get("SaleOrderType"),
            "订单是否关闭": "是" if order.get("is_closed") else "否",
            "订单批准时间": order.get("ApproveTime"),
            "订单确认时间": order.get("ConfirmDate"),
        }
        # 单采信息
        apheresis_list = order.get("Apheresis", [])
        if apheresis_list:
            for aph in apheresis_list:
                row_ap = row.copy()
                row_ap.update({
                    "单采编号": aph.get("DanCaiNo"),
                    "单采计划日期": aph.get("plan_apheresis_date"),
                    "单采实际日期": aph.get("apheresis_date"),
                    "单采开始时间": aph.get("apheresis_start"),
                    "单采结束时间": aph.get("apheresis_end"),
                    "单采状态": aph.get("order_status"),
                    "单采是否关闭": "是" if aph.get("is_closed") else "否",
                    "单采样本到达时间": aph.get("Apheresis_ArrivalDate"),
                    "单采样本放行时间": aph.get("Apheresis_ReleaseDate"),
                })
                # 生产批次信息
                prod_batch_list = aph.get("ProdBatch", [])
                if prod_batch_list:
                    for pb in prod_batch_list:
                        row_pb = row_ap.copy()
                        row_pb.update({
                            "生产批次编码": pb.get("ProdBatchCode"),
                            "车间名称": pb.get("WorkshopName"),
                            "技术标准名称": pb.get("TechniqueStandardName"),
                            "生产批次状态": pb.get("ProdBatchStatus"),
                            "生产审核日期": pb.get("AuditDate"),
                            "工序名称": pb.get("ProcName"),
                            "生产开始时间": pb.get("WorkStartTime"),
                            "生产结束时间": pb.get("WorkEndTime"),
                        })
                        # 产品放行信息
                        product = pb.get("Product", {})
                        row_pb.update({
                            "COA编号": product.get("COANo"),
                            "质量状态": product.get("QualityStatus"),
                            "制药快速放行人员": product.get("制药快速放行"),
                            "制药快速放行日期": product.get("制药快速放行日期"),
                            "MAH快速放行人员": product.get("MAH快速放行"),
                        })
                        result.append(row_pb)
                else:
                    # 没有生产批次
                    result.append(row_ap)
        else:
            # 没有单采信息
            result.append(row)

# 3. 打印结果
print(result)