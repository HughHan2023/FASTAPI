import pandas as pd

result = {"a":123,"b":456,"c":{"d":1,"e":{"f":1,"g":2}}}
# 使用pandas的json_normalize展开嵌套字典
result = pd.json_normalize(result)


# r=pd.DataFrame(result)
print(result)






