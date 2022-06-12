import requests
import re
import os
from itertools import compress
from utils import *

url = 'https://sspai.com/feed'
raw = requests.get(url).text
all = re.findall(r'<item><title>(.*?)</title><link>(.*?)</link><description>(.*?)</description><author>(.*?)</author><pubDate>(.*?)</pubDate></item>', raw, re.S)
keywords_list = ["饭","吃","食"]
fil = [any(f in x[0] for f in keywords_list) for x in all]
food = list(compress(all,fil))

checkpoint = '/tmp/food.data'
if os.path.exists(checkpoint):
    with open(checkpoint) as fp:
        data = fp.read()
        if data == food[0][1]:
            os.exit(0)
with open(checkpoint, 'w') as fp:
    fp.write(food[0][1])

msg = {"msg_type": "post", "content": {"post": {
                        "zh_cn": {
                                "title": "少数派做饭推荐",
                                "content": [
                                        
                                        [
                                            {"tag": "text", "text": food[0][0]},
                                            {
                                                        "tag": "a",
                                                        "text": "\n查看原文",
                                                        "href": food[0][1]
                                                },
                                        ]
                                ]
                        }
                }
        }
}

print(msg)
requests.post(WEATHER_ROBOT_URL, json=msg)
