from distutils.file_util import move_file
import re
from bs4 import BeautifulSoup
import requests
from api import MessageApiClient

douban_hint = '请输入豆瓣电影的链接。'

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39',
}
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

    content = {
        "标签": genre_list,
        "状态": "待看",
        "年份": int(year),
        "豆瓣链接": {'text': url, 'link': url},
        "导演": director,
        "主演": actors,
        "豆瓣评分": float(rating),
    #     "海报": [{'file_token': 'boxcnH7iSLRxltn9bguJIWr1Vxf',
    #         'name': 'image.png',
    #         'type': 'image/png',
    #         'size': 865947,
    #         'url': 'https://open.feishu.cn/open-apis/drive/v1/medias/boxcnH7iSLRxltn9bguJIWr1Vxf/download',
    #         'tmp_url': 'https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url?file_tokens=boxcnH7iSLRxltn9bguJIWr1Vxf'}],
        "片名":name,
    }
    return content


class NewMovie:
    def __init__(self):
        self.adding = False
    
    def isAdding(self):
        self.adding = True
        return self.adding

    def add(self, url):
        self.movie_content = douban_info(url)
        return self.movie_content


class DoubanModule2:
    def __init__(self):
        self.m = NewMovie()


    def Handle(self, content, **kvargs):
        if content == '甜甜看片':
            self.m.isAdding()
            return douban_hint
        
        if self.m.adding:
            c = MessageApiClient()
            c.new_bittable_records('bascn8PCizNlokom09WfnN89O3b','tblMha0FYWopst7m', self.m.add(content))
            return '已添加'
        
        return None


class DoubanModule:
    def __init__(self) -> None:
        pass

    def Handle(self, content):
        if content.startswith('甜甜看片'):
            c = MessageApiClient()
            url = content.split(sep=' ')[1]
            detail = douban_info(url)
            c.new_bittable_records('bascn8PCizNlokom09WfnN89O3b','tblMha0FYWopst7m', detail)
            return '已添加'
 
            



if __name__ == '__main__':
    m = DoubanModule()
    # print(m.Handle('甜甜看片'))
    # print(m.Handle('https://movie.douban.com/subject/27046758/'))
    print(m.Handle('甜甜看片 https://movie.douban.com/subject/27046758/'))