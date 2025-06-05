import requests
import json

# 目标URL（请替换为实际的API端点）
# url = "http://192.168.15.83:8080/execute"
url = "http://localhost:8080/execute"


# 要发送的JSON数据
data = {
    "code": "```python\nimport json\nimport urllib.request\nfrom collections import defaultdict\nimport matplotlib.pyplot as plt\n\n# 获取JSON数据\nurl = \"http://192.168.15.147:8004/TraceData.json\"\nwith urllib.request.urlopen(url) as response:\n    data = json.loads(response.read().decode('utf-8'))\n\n# 统计4月和5月的订单数量\nmonthly_orders = defaultdict(int)\n\nfor order in data:\n    order_date = order['SaleOrderDate']\n    month = int(order_date.split('-')[1])  # 提取月份部分\n    if month in [4, 5]:\n        monthly_orders[month] += 1\n\n# 准备饼图数据\nlabels = ['April', 'May']\nsizes = [monthly_orders[4], monthly_orders[5]]\ncolors = ['#ff9999', '#66b3ff']\nexplode = (0.05, 0)  # 突出显示第一个扇形\n\n# 绘制饼图\nplt.figure(figsize=(8, 8))\nplt.pie(sizes, explode=explode, labels=labels, colors=colors, \n        autopct='%1.1f%%', startangle=90, shadow=True)\nplt.title('Orders Distribution in April and May')\nplt.axis('equal')  # 保证饼图是圆形\n\n# 将图表对象存入result并显示\nresult = plt\nresult.show()\n```"
}

# 设置请求头，指定内容类型为JSON
headers = {
    "Content-Type": "application/json"
}

try:
    # 发送POST请求
    response = requests.post(url, data=json.dumps(data), headers=headers)
    
    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功!")
        print("响应内容:", response.json())
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print("响应内容:", response.text)
except requests.exceptions.RequestException as e:
    print("请求发生错误:", e)