## 用bs4做的小机器人0.2
import requests
from bs4 import BeautifulSoup as bs
from api import MessageApiClient
from utils import *

cookie='_zap=2617c044-450d-4db5-9e59-7f7f8bb8c3bf; d_c0="ACCWaGUdABGPTqFQBK7F9x_2OSrc4a7SAvs=|1584845482"; _ga=GA1.2.25523070.1584845506; _xsrf=c4754411-05b9-4c0b-8d4e-cd6620086905; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1641654840,1641693447,1641778785,1642213577; captcha_session_v2="2|1:0|10:1642213577|18:captcha_session_v2|88:SzJMdnNEbTVXWGNkMVBlRnRabElpOGl1ZDlQbFZVcGZEbzk0UHRLZ01GOTh1LzVsT3dNSkJ0Tm96bHdiVDBkcg==|2c308b91149bcd767048f46eea73780f1c51a6fd2531171114b8a514792f2156"; _gid=GA1.2.1608353969.1642933592; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1642934699; KLBRSID=0a401b23e8a71b70de2f4b37f5b4e379|1642934777|1642933589; _gat=1'

headers = {
    'Cookie': cookie,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
}
url = 'https://daily.zhihu.com/'

message_api_client = MessageApiClient()

def ans(in_answer):
   return "\n".join([x.text.strip() for x in in_answer])

def tag_text(text):
    return {'tag': 'text', 'text': text}

def upload_image_to_feishu(image_path: str):
    if image_path.startswith('img_v2_'):
        return image_path
    try:
        data = requests.get(image_path).content
        with open('/tmp/sample.jpg', 'wb') as fp:
            fp.write(data)
        return message_api_client.upload_image('/tmp/sample.jpg')
    except:
        return 'img_v2_868f1042-efb9-4973-93db-9c71f1015a6g'

def tag_image(img):
    return {'tag': 'img', 'image_key': upload_image_to_feishu(img)}

def gen_answers(question):
    answers = list(question.find_all('div', class_='content'))
    
    tags = []
    for answer in answers:
        for i, c in enumerate(answer):
            img = c.find('img')
            content = c.text.strip()
            if img and img != -1:
                # 存在图片，转换成图片
                tags.append([tag_image(img.attrs['src'])])
            elif content:
                tags.append([tag_text(content)])
                
    if tags:
        tags[0] = [tag_text('A: ')] + tags[0]
    else:
        tags = [[tag_text('A: ')]]
        
    tags[-1].append(tag_text(' \n\n')) # 最后添加一个换行
    
    return tags
    
def gen_question(question):
    title = question.find('h2',class_='question-title').text
    answer_tags = gen_answers(question)
    return [[tag_text('Q: ' + title)]] + answer_tags

r = requests.get(url, headers=headers)
soup = bs(r.content)
all = soup.find_all('a',class_='link-button')
l = [[a['href'], a.find('span').text] for a in all ]
url_xiache = [ x[0] for x in l if '瞎扯' in x[1]][0]
with open('/tmp/xiache.txt','r') as f:
    last_line = f.readline()

if (url_xiache != last_line):
    with open('/tmp/xiache.txt','w') as f:
        f.write(url_xiache)

    url_xiache_s = 'https://daily.zhihu.com{}'.format(url_xiache)
    r_xiache = requests.get(url_xiache_s, headers=headers)
    div_xiache = bs(r_xiache.content).div
    questions = [x for x in div_xiache.find_all('div',class_='question')]
    question_tags = []
    for question in questions:
        question_tags.extend(gen_question(question))

    msg = {"msg_type": "post", "content": {"post": {
                            "zh_cn": {
                                    "title": "工作日摸鱼时刻",
                                    "content": question_tags + [                              
                                            [
                                                
                                                {
                                                            "tag": "a",
                                                            "text": "瞎扯 · 如何正确地吐槽",
                                                            "href": url_xiache_s
                                                    }
                                            ]
                                            
                                    ]
                            }
                    }
            }
    }
    resp = requests.post(SWIM_ROBOT_URL, json=msg)
    print(resp.content)

