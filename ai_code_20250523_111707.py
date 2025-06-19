import json
import urllib.request
from datetime import datetime

def main():
    # 下载并解析JSON数据
    url = "http://192.168.15.83:8080/static/TraceData.json"
    response = urllib.request.urlopen(url)
    data_bytes = response.read()
    data_str = data_bytes.decode("utf-8")
    data = json.loads(data_str)

    # 统计2025年4月的订单数量
    target_year = 2025
    target_month = 4
    count = 0

    # 提取订单日期字段
    sale_order_date = data.get("SaleOrderDate")
    
    # 验证日期是否符合目标年月
    if sale_order_date:
        try:
            order_date = datetime.strptime(sale_order_date, "%Y-%m-%d")
            if (order_date.year == target_year and 
                order_date.month == target_month):
                count = 1  # 单个订单
        except ValueError:
            # 日期格式错误时忽略该记录
            pass

    result = count
    print(result)

if __name__ == "__main__":
    main()