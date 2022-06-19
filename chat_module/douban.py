from distutils.file_util import move_file
import re
from bs4 import BeautifulSoup
import requests
from api import MessageApiClient

douban_hint = '请输入豆瓣电影的链接。'

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39',
}


def upload_image_to_feishu(image_path: str):
    try:
        data = requests.get(image_path).content
        with open('/tmp/sample.jpg', 'wb') as fp:
            fp.write(data)
        return message_api_client.upload_image('/tmp/sample.jpg')
    except:
        return 'img_v2_868f1042-efb9-4973-93db-9c71f1015a6g'


def douban_info(url):
    r = requests.get(url, headers = headers).content
    soup = BeautifulSoup(r, 'html.parser')
    name = soup.h1.span.contents[0]
    year = soup.h1.find('span', class_ = 'year').contents[0][1:-1]
    info = soup.find('div',id = 'info')
    genre_list = [genre.contents[0] for genre in info.find_all('span', property = 'v:genre')]
    director = info.span.contents[-1].a.contents[0]
    actors ='，'.join([x.contents[0] for x in info.find('span', class_='actor').find_all('a')])
    rating = soup.strong.contents[0]
    pic_url = soup.find('a', class_ = 'nbgnbg').contents[1]['src']


    content = {
        "标签": genre_list,
        "状态": "待看",
        "年份": int(year),
        "豆瓣链接": {'text': url, 'link': url},
        "导演": director,
        "主演": actors,
        "豆瓣评分": float(rating),
        "片名":name,
    }
    return content, pic_url


class DoubanModule:
    def __init__(self) -> None:
        pass

    def Handle(self, content):
        if content.startswith('甜甜看片'):
            c = MessageApiClient()
            url = content.split(sep=' ')[1]
            detail, img_url = douban_info(url)
            detail['海报']=[{"file_token": c.upload_medias(img_url)}]
            c.new_bittable_records('bascn8PCizNlokom09WfnN89O3b','tblMha0FYWopst7m', detail)
            return f'已添加《{detail["片名"]}》'
 
            



if __name__ == '__main__':
    m = DoubanModule()
    # print(m.Handle('甜甜看片'))
    # print(m.Handle('https://movie.douban.com/subject/27046758/'))
    print(m.Handle('甜甜看片 https://movie.douban.com/subject/27046758/'))