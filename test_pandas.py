import json
import pandas as pd

with open('test2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)


df['numberOfTransfusion'] = df['Transfusion'].apply(lambda x: len(x))
df['numberOfApheresis'] = df['Apheresis'].apply(lambda x: len(x))
df['numberOfProdBatch'] = df['Apheresis'].apply(lambda x: sum(len(apheresis.get('ProdBatch', [])) for apheresis in x))
df['order_status'] = df['Apheresis'].apply(lambda x: x[0]['order_status'] if x and 'order_status' in x[0] else None)




df.to_json('test3.json', orient='records')