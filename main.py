import json
import os

os.listdir('')
with  open('driver/KIA/Kia_Carnival/Kia_Carnival3623.json') as f:
    data = json.load(f)
    print(data)
