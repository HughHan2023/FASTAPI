import re
ruf={
  "arg1": "```python\nimport json\nfrom urllib.request import urlopen\nfrom datetime import datetime\n\n# 获取JSON数据\nwith urlopen(\"http://192.168.15.83:8080/static/TraceData.json\") as response:\n    data = json.loads(response.read().decode('utf-8'))\n\ncount_failed_batches = 0\n\nfor order in data:\n    # 检查每个订单中的生产批次\n    if \"Apheresis\" in order:\n        for apheresis in order[\"Apheresis\"]:\n            if \"ProdBatch\" in apheresis:\n                for batch in apheresis[\"ProdBatch\"]:\n                    # 筛选2025年的批次\n                    if \"AuditDate\" in batch and batch[\"AuditDate\"]:\n                        try:\n                            audit_date = datetime.strptime(batch[\"AuditDate\"], \"%Y-%m-%d %H:%M:%S\")\n                            if audit_date.year == 2025:\n                                # 检查是否是生产终止或者不予放行\n                                if (batch.get(\"ProdBatchStatus\") == \"生产终止\" or \n                                    (\"Product\" in batch and batch[\"Product\"].get(\"QualityStatus\") == \"不予放行\")):\n                                    count_failed_batches += 1\n                        except ValueError:\n                            continue\n\n# 存储结果\nresult = count_failed_batches\nprint(result)\n```"
}
arg1=ruf.get("arg1")

def main(arg1: str) -> dict:
    matches = re.findall(r"```python(.*?)```", arg1, re.DOTALL)
    raw_code = matches[0].strip()
    print(raw_code)
if __name__ == "__main__":
    main(arg1)