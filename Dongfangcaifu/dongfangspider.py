# -- coding: utf-8 --
# @Time : 2021/3/7 19:20
# @Author : Los Angeles Clippers
# @Email: 229456906@qq.com
# @sinaemail: angelesclippers@sina.com


import requests
import re
import json
import csv
import os


headers = {
    'Referer': 'https://vipmoney.eastmoney.com/collect/stockranking/pages/ranking/list.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}


def getUtandeFields() ->dict:
    ut_fields = {}
    url = "https://vipmoney.eastmoney.com/collect/stockranking/static/script/ranking_list.js?01211021_1.0.2"
    params = {
        '01211021_1.0.2': ''
    }
    response = requests.get(url, headers=headers, params=params).text
    ut_fields['ut'] = re.search(r'ut:"(.*?)"', response).group(1)
    ut_fields['fields'] = re.search(r'fields:"(.*?)"', response).group(1)
    ut_fields['globalId'] = re.search(r'globalId:"(.*?)"', response).group(1)
    return ut_fields

def getSecids(ut_fields: dict) ->str:
    url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
    headers['Host'] = "emappdata.eastmoney.com"
    headers['Origin'] = "https://vipmoney.eastmoney.com"
    data = {
        'appId': 'appId01',
        'globalId': ut_fields['globalId'],
        'pageNo': '1',
        'pageSize': '100',
    }
    response = requests.post(url, json=data, headers=headers).text
    jsData = json.loads(response)['data']
    secids = ""
    gb = 0
    for item in jsData:
        gb += 1
        sc = item['sc']
        if "SH" in sc:
            secids += sc.replace("SH", "1.") + ","
            if gb == len(jsData):
                secids += sc.replace("SH", "1.")
        else:
            secids += sc.replace("SZ", "0.") + ","
            if gb == len(jsData):
                secids += sc.replace("SZ", "0.")
    return secids


def getData(ut_fields, secids) ->dict:
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?"
    headers['Host'] = "push2.eastmoney.com"
    data = {
        'ut': ut_fields['ut'],
        'fltt': '2',
        'invt': '2',
        'fields': ut_fields['fields'],
        'secids': secids,
    }
    response = requests.post(url, data=data, headers=headers).text
    jsData = json.loads(response)['data']['diff']
    savepath = os.getcwd() + r'\data'
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    fp = open(savepath + r'\ulist.csv', 'w', encoding='utf-8', newline='')
    fw = csv.writer(fp)
    fw.writerow(['排名', '股票名称', '股票代码', '现价', '涨跌幅'])
    i = 0
    srcSecurityCode_dict = {}
    for item in jsData:
        i += 1
        paiming = i       # 排名
        name = item['f14']          # 股票名称
        xianjia = item['f2']        # 现价
        daima = item['f12']         # 股票代码
        zdf = item['f3']            # 涨跌幅
        content = [paiming, name, daima, xianjia, zdf]
        fw.writerow(content)

        f13 = int(item['f13'])
        if f13 == 1:
            srcSecurityCode_dict[name] = "SH" + str(daima)
        else:
            srcSecurityCode_dict[name] = "SZ" + str(daima)
    return srcSecurityCode_dict


def getCurrentList(srcSecurityCode_dict, ut_fields):
    savepath = os.getcwd() + r'\CurrentListData'
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    url = "https://emappdata.eastmoney.com/stockrank/getCurrentList"
    headers['Host'] = 'emappdata.eastmoney.com'
    data = {
        'appId': 'appId01',
        'globalId': ut_fields['globalId'],
        'srcSecurityCode': '',
    }
    for name, srcSecurityCode in srcSecurityCode_dict.items():
        if '*' in name:
            name = name.replace('*', '')
        else:
            name = name
        fp = open(savepath + r'\【{}】实时排名.csv'.format(name), 'w', encoding='utf-8', newline='')
        fw = csv.writer(fp)
        fw.writerow(['股票名称', '股票代码', '时间点', '排名'])

        data['srcSecurityCode'] = srcSecurityCode
        response = requests.post(url, json=data, headers=headers).text
        jsData = json.loads(response)['data']
        print(jsData)
        saveCurrentList(jsData, name, srcSecurityCode, fw)

def saveCurrentList(jsData, name, srcSecurityCode, fw):
    for item in jsData:
        fw.writerow([name, srcSecurityCode, str(item['calcTime']), str(item['rank'])])


def getHisList(srcSecurityCode_dict, ut_fields):
    savepath = os.getcwd() + r'\HisListData'
    if not os.path.exists(savepath):
        os.mkdir(savepath)
    url = "https://emappdata.eastmoney.com/stockrank/getHisList"
    headers['Host'] = 'emappdata.eastmoney.com'
    data = {
        'appId': 'appId01',
        'globalId': ut_fields['globalId'],
        'srcSecurityCode': '',
    }
    for name, srcSecurityCode in srcSecurityCode_dict.items():
        if '*' in name:
            name = name.replace('*', '')
        else:
            name = name
        fp = open(savepath + r'\【{}】历史排名.csv'.format(name), 'w', encoding='utf-8', newline='')
        fw = csv.writer(fp)
        fw.writerow(['股票名称', '股票代码', '时间点', '排名'])

        data['srcSecurityCode'] = srcSecurityCode
        response = requests.post(url, json=data, headers=headers).text
        jsData = json.loads(response)['data']
        print(jsData)
        saveCurrentList(jsData, name, srcSecurityCode, fw)



if __name__ == '__main__':
    ut_fields = getUtandeFields()
    print(ut_fields)
    secids = getSecids(ut_fields)
    print(secids)
    srcSecurityCode_dict = getData(ut_fields, secids)
    print(srcSecurityCode_dict)
    getCurrentList(srcSecurityCode_dict, ut_fields)
    getHisList(srcSecurityCode_dict, ut_fields)