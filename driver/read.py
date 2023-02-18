import json
import os
import codecs

text = "new"

with codecs.open("KIA/Kia_Carnival/Kia_Carnival3623.json", 'r', encoding='cp1251') as f:
    data = json.load(f)
    secure = data["auto"]["images"][::-1]
    print(secure)