from bs4 import BeautifulSoup
import requests
from api import MessageApiClient

podcast_hint = '请输入小宇宙播客的链接。'
podcast_feishu_node_id = 'bascnLfGfmHxVcpx7tbJK4gWkGf'

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

def podcast_info(url):
    r = requests.get(url, headers = headers).content
    soup = BeautifulSoup(r, 'html.parser')
    ep_title = soup.main.header.h1.contents[0]
    pod_title = soup.main.a.contents[0]
    ep_img_url = soup.main.header.find_all('img')[0]['src']
    # ep_img_token = c.upload_medias(ep_img_url)
    pod_img_url = soup.main.header.find_all('img')[1]['src']
    # pod_img_token = c.upload_medias(pod_img_url)
    duration = soup.main.header.find_all('div')[2].contents[2]
    date = soup.main.header.find_all('div')[2].contents[6]['datetime'][0:10]
    all_contents = soup.main.article.contents
    cont = '\n'.join([line.text for line in all_contents])
    # audio_url = soup.head.find_all('meta')[-5]['content']
    # audio_token = c.upload_medias(audio_url)
    content = {
        "单集名称": ep_title,
        "播客名称": pod_title,
        "日期": date,
        "时长": duration,
        "链接":{'text': url, 'link': url},
        "shownotes": cont,
        # "附件": [
        #     {"file_token": audio_token}
        # ]


    }
    return content, ep_img_url, pod_img_url


class PodcastModule:
    def __init__(self) -> None:
        pass

    def Handle(self, content):
        if content.startswith('甜甜宇宙'):
            c = MessageApiClient()
            url = content.split(sep=' ')[1]
            detail, ep_img_url, pod_img_url = podcast_info(url)
            detail['单集封面']=[{"file_token": c.upload_medias(ep_img_url, parent_node=podcast_feishu_node_id)}]
            detail['播客封面']=[{"file_token": c.upload_medias(pod_img_url, parent_node=podcast_feishu_node_id)}]
            c.new_bittable_records(podcast_feishu_node_id,'tblNZSZ8iu2Yp8ry', detail)
            return f'已添加《{detail["单集名称"]}》'

if __name__ == '__main__':
    m = PodcastModule()
    print(m.Handle('甜甜宇宙 https://www.xiaoyuzhoufm.com/episode/62a176dfcd9b181e67a2f02e'))