import json
from datetime import datetime

def count_orders_in_april_2025(data):
    target_year = 2025
    target_month = 4
    order_set = set()
    
    for record in data:
        sale_order_date = record.get("SaleOrderDate")
        if not sale_order_date:
            continue
            
        try:
            order_date = datetime.strptime(sale_order_date, "%Y-%m-%d")
        except ValueError:
            continue
            
        if (order_date.year == target_year and order_date.month == target_month):
            order_set.add(record["SaleOrderNo"])
            
    return len(order_set)

def main():
    # 模拟从URL获取数据，实际应使用urllib或requests获取
    # 这里用示例数据代替
    data = [
        {
            "SaleOrderNo": "CLS-24-0001",
            "SaleOrderDate": "2025-04-15"
        },
        {
            "SaleOrderNo": "CLS-25-0002",
            "SaleOrderDate": "2025-04-01"
        },
        {
            "SaleOrderNo": "CLS-25-0003",
            "SaleOrderDate": "2025-04-30"
        },
        {
            "SaleOrderNo": "CLS-25-0004",
            "SaleOrderDate": "2025-05-01"
        },
        {
            "SaleOrderNo": "CLS-25-0005",
            "SaleOrderDate": None
        }
    ]
    
    result = count_orders_in_april_2025(data)
    print(f"2025年4月订单数: {result}")

if __name__ == "__main__":
    main()