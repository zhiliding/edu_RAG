# import json
# with open('model_generic_5000.json', "r", encoding="utf-8") as f:
#     data = [json.loads(value) for value in f.readlines()] # 等价：f.readlines()
#
# print(data[0])
# print(type(data[0]))
import numpy as np

a = np.array([[0.2, 0.8],
              [0.7, 0.3],
              [0.68, 0.32],
              [0.25, 0.75],
              [0.71, 0.29]])
print(a.shape)
labels = np.array([0, 1, 1, 1, 0])
b = np.argmax(a,axis=-1)
print(f'b--->{b}')
print(labels.shape)
print((b == labels).mean())