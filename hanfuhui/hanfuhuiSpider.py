# -- coding: utf-8 --
# @Time : 2021/3/7 22:18
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com

import requests
import re
import os
import json
from lxml import etree

"""
https://www.hanfuhui.com/
"""


def get_IDList():
    url = 'https://api5.hanfugou.com/Trend/GetTrendListForHot?'
    headers = {
        'origin': 'https://www.hanfuhui.com',
        'referer': 'https://www.hanfuhui.com/',
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }
    data = {
        'maxid': '0',
        'objecttype': 'video',
        'page': '1',
        'count': '20',
    }
    i = 0
    for page in range(1, 10000000):
        if page != 1:
            data['maxid'] = str(3045525)
        data['page'] = page
        response = requests.get(url, params=data, headers=headers).text
        jsData = json.loads(response)['Data']
        if len(jsData) == 0:
            break
        for item in jsData:
            i += 1
            id = item['ID']
            indexUrl = 'https://www.hanfuhui.com/Details/' + str(id)
            print(indexUrl)
            saveVideos(indexUrl, i)
        # break


def saveVideos(indexUrl, i):
    headers = {
        'referer': 'https://www.hanfuhui.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }
    response = requests.get(indexUrl, headers=headers).text
    videoUrl = re.search(r'js_videoplay", ".*?", "(.*?)"', response).group(1)
    print(videoUrl)
    _upt = re.search(r'_upt=(.*?)"', response).group(1)
    with open('videoData/{}.mp4'.format(_upt), 'wb') as f:
        f.write(requests.get(videoUrl, headers=headers).content)
        f.close()
    print('第{}个视频保存成功！'.format(i))


if __name__ == '__main__':
    if not os.path.exists(os.getcwd() + r'\videoData'):
        os.mkdir(os.getcwd() + r'\videoData')
    get_IDList()
