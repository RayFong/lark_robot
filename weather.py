import requests
import re

url = 'https://tianqi.moji.com/today/china/shanghai/yangpu-district'
raw = requests.get(url).text

detail_time = re.search(r'<div class="detail_time clearfix">(.*?)</div>', raw, re.S).group(1).split()[0]
day_details = re.findall(r'<div class="day">(.*?)</div>', raw, re.S)

light, night = day_details[0], day_details[1]
weather = re.search(r'<em>(.*?)</em>', light, re.S).group(1).strip()
light_temp = re.search(r'<b>(.*?)</b>', light, re.S).group(1).strip()
night_temp = re.search(r'<b>(.*?)</b>', night, re.S).group(1).strip()

sun_up = re.search(r'<strong>(.*?)</strong>', light, re.S).group(1).strip()
sun_down = re.search(r'<strong class="sun_down">(.*?)</strong>', night, re.S).group(1).strip()

description = re.search(r'<meta name="description" content="(.*?)">', raw, re.S).group(1)
humidity = description.split(sep='。')[0].split(sep='，')[1]
wind = description.split(sep='。')[0].split(sep='，')[2]

wea15 = re.findall(r'<li  >(.*?)</li>', raw, re.S)
pre = re.findall(r'<span class="wea">(.*?)</span>', wea15[0], re.S)
pre_temp_day = re.search(r'<b>(.*?)</b>', wea15[0], re.S).group(1)
pre_temp_night = re.search(r'<strong>(.*?)</strong>', wea15[0], re.S).group(1)

msg = {"msg_type": "post", "content": {"post": {
                        "zh_cn": {
                                "title": f"{detail_time}",
                                "content": [
                                        [
                                            {"tag": "text", "text": f"今天天气: {weather}"}
                                        ],
                                        [
                                            {"tag": "text", "text": f"温度: {night_temp} ~ {light_temp}"}
                                        ],
                                        [
                                            {"tag": "text", "text": f"{sun_up}, {sun_down}"}
                                        ],
                                        [
                                            {"tag": "text", "text": f"{wind}"}
                                        ],
                                        [
                                            {"tag": "text", "text": f"{humidity}"}
                                        ],
                                        [
                                            {"tag": "text", "text": "详情查看: "},
                                            {
                                                        "tag": "a",
                                                        "text": "杨浦区今日状况",
                                                        "href": url
                                                },
                                        ],
                                        [
                                            {"tag": "text", "text": f"昨天白天{pre[0]} {pre_temp_day}"}
                                        ],
                                        [
                                            {"tag": "text", "text": f"昨天夜间{pre[1]} {pre_temp_night}"}
                                        ]
                                ]
                        }
                }
        }
}

print(msg)
requests.post('https://open.feishu.cn/open-apis/bot/v2/hook/f98a3cd9-25a7-4bc1-800b-12f82729ce08', json=msg)
