from bs4 import BeautifulSoup
import requests
import json
import os
import logging 


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


def save_data(filepath, data):
    with open(filepath, 'w') as fp:
        d = json.dumps(data, ensure_ascii=False, indent=2)
        fp.write(d)


def load_data(filepath, default={}):
    if not os.path.exists(filepath):
        return default
    with open(filepath) as fp:
        return json.load(fp)


def fetch_idiom_by_index(idx):
    url = f'http://www.zd9999.com/cy/htm{idx//10000}/{idx}.htm'
    if idx % 100 == 0:
        log.info('fetching=%s', url)

    html = requests.get(url)
    idiom_bs = BeautifulSoup(html.content.decode('gbk', errors='ignore'), "html.parser")
    idiom_metas = idiom_bs.find_all('table')[-3].find_all('tr')
    idiom_fields = idiom_metas[1].find_all('tr')

    return {
        'index': idx,
        'url': url,
        'word': idiom_metas[0].text.strip(),
        'pingyin': idiom_fields[0].find_all('td')[-1].text.strip()
    }


def download_multi_idioms(idx_iter):
    all_datas, failed_result = [], []
    for idx in idx_iter:
        try:
            idiom_data = fetch_idiom_by_index(idx)
            all_datas.append(idiom_data)
        except Exception as e:
            log.error('fetch=%s failed, err=%s', idx, str(e))
            failed_result.append({'index': idx, 'failed_reason': str(e)})
    return all_datas, failed_result
    

def idiom_downloader(max_index=31648, data_path='./'):
    success_path = os.path.join(data_path, 'idioms.json')
    failed_path = os.path.join(data_path, 'failed_idioms.json')

    all_datas = load_data(success_path, default=[])
    loaded_max_index = max(all_datas, key=lambda x: x['index'], default={'index':0})['index']
    log.info('Starting Index=%d', loaded_max_index)

    failed_result = []
    for idx in range(loaded_max_index+1, max_index+1):
        try:
            idiom_data = fetch_idiom_by_index(idx)
            all_datas.append(idiom_data)
        except Exception as e:
            log.error('fetch=%s failed, err=%s', idx, str(e))
            failed_result.append({'index': idx, 'failed_reason': str(e)})

        if idx % 200 == 0:
            save_data(success_path, all_datas)
            save_data(failed_path, failed_result)

    save_data(success_path, all_datas)
    save_data(failed_path, failed_result)


if __name__ == '__main__':
    idiom_downloader()
