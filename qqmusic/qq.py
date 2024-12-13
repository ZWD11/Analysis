import requests
import time
import execjs
import csv
import json
import string
import random
import re


search = input("请输入搜索内容：")
cookies = {
    "RK": "7fNkvDBTwb",
    "ptcz": "1ddcaa51ae4b330943f04da8cb71d15abbf101a8bb9b584034bacb00fe4f03a7",
    "pac_uid": "0_NDMWPyH26Bh93",
    "_qimei_uuid42": "1870a0e2810100d23ee5195cfaa33f3353bfdcf749",
    "_qimei_fingerprint": "777996e6dd860eabb134801164e4348b",
    "_qimei_h38": "17ac91663ee5195cfaa33f3302000007e1870a",
    "pgv_pvid": "6393809020",
    "fqm_pvqid": "9b786063-e67e-4f13-b742-e945ace2c473",
    "ts_uid": "5568342188",
    "qq_domain_video_guid_verify": "15bfd62d6b44e0b2",
    "suid": "user_0_NDMWPyH26Bh93",
    "o_cookie": "3107412944",
    "_qimei_q32": "1912b3d0dd897b5a188cf0bfca1f3c13",
    "_qimei_q36": "ca7a515961fc4dee486ccd17300015a17c0a",
    "yq_index": "2",
    "music_ignore_pskey": "202306271436Hn@vBj",
    "ts_refer": "cn.bing.com/",
    "qm_keyst": "Q_H_L_63k3NdavdbN9Wt-ltw9qebxgQikK0Ezkp6uzQAmCVQ9VjL8i_QwDB6ItNmlbzx2-eyW3lcJ0fFaDQ1MBeHI3tzvSlQWA",
    "euin": "oi6z7iv5owEP7n**",
    "psrf_qqaccess_token": "7E4BC0B80CC87E9451A36B4691AB7D8C",
    "psrf_qqopenid": "C0865D9CE8FDF326F5C4C134A5D0012C",
    "psrf_musickey_createtime": "1733813461",
    "psrf_qqrefresh_token": "9F3810C348443ECBB42CB2E1C5774E33",
    "wxunionid": "",
    "wxrefresh_token": "",
    "psrf_qqunionid": "A4968FF9F8E4CD54398FC3897660C0DA",
    "wxopenid": "",
    "qqmusic_key": "Q_H_L_63k3NdavdbN9Wt-ltw9qebxgQikK0Ezkp6uzQAmCVQ9VjL8i_QwDB6ItNmlbzx2-eyW3lcJ0fFaDQ1MBeHI3tzvSlQWA",
    "uin": "3107412944",
    "tmeLoginType": "2",
    "psrf_access_token_expiresAt": "1734418261",
    "fqm_sessionid": "1dce0595-fe71-4276-8e75-1df31e6eb120",
    "pgv_info": "ssid=s4817944160",
    "ts_last": "y.qq.com/"
}
headers = {
    "^accept": "*/*^",
    "^accept-language": "zh-CN,zh;q=0.9^",
   # "^cookie": "pgv_pvid=5312633750; fqm_pvqid=0acd4170-e201-4f5e-86c7-ecd1bd0d8fce; fqm_sessionid=8a72e12e-3309-45f7-abdf-7a56a69fe509; pgv_info=ssid=s3422272799; ts_refer=cn.bing.com/; ts_uid=6790548262; _qpsvr_localtk=0.22222730411303693; RK=UfNkujBCn7; ptcz=ff2251b7622b54728b11e8272c1535dc50cce5fa5af13fbe9da72d8b8f89c180; euin=oi6z7iv5owEP7n**; tmeLoginType=2; music_ignore_pskey=202306271436Hn^@vBj; psrf_musickey_createtime=1732786192; psrf_access_token_expiresAt=1733390992; qqmusic_key=Q_H_L_63k3Nrk1SfR4VYNt3t8O4gLcJB-5qrHnGzYuQY9idN08oiApheqeMhgJNMVrw-aRvl_hkzJHwpsuG1YjRUqVSKkPjzFQ; ts_last=y.qq.com/n/ryqq/toplist/4^",
    "^priority": "u=1, i^",
    "^referer": "https://y.qq.com/^",
    "^sec-ch-ua": "^\\^Chromium^^;v=^\\^130^^, ^\\^Microsoft",
    "^sec-ch-ua-mobile": "?0^",
    "^sec-ch-ua-platform": "^\\^Windows^^^",
    "^sec-fetch-dest": "empty^",
    "^sec-fetch-mode": "cors^",
    "^sec-fetch-site": "same-site^",
    "^user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0^",
    "^origin": "https://y.qq.com^",
    "^content-type": "text/plain;charset=UTF-8^"
}
url = "https://u6.y.qq.com/cgi-bin/musics.fcg"

headers_mobile = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 Edg/123.0.0.0',
    'Referer': 'https://y.qq.com/',
}

#data = '{"comm":{"cv":4747474,"ct":24,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"yqq.json","needNewCode":1,"uin":0,"g_tk_new_20200303":238868454,"g_tk":238868454},"req_1":{"module":"musicToplist.ToplistInfoServer","method":"GetDetail","param":{"topid":4,"offset":0,"num":20,"period":""}}}'
data1 = json.dumps(
    {"comm": {
        "cv": 4747474,
        "ct": 24,
        "format": "json",
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq.json",
        "needNewCode": 1,
        "uin": cookies['uin'],
        "g_tk_new_20200303": 733072917,
        "g_tk": 733072917
    },
    "req_1": {
        "method": "DoSearchForQQMusicDesktop",
        "module": "music.search.SearchCgiService",
        "param": {
            "remoteplace": "txt.yqq.center",
            "searchid": "".join(random.sample(string.digits + string.digits, 17)),
            "search_type": 0,
            "query": search,
            "page_num": 1,
            "num_per_page": 30
        }
    }
})
with open("./loader.js", 'r', encoding="utf-8") as f:
    js_code = f.read()

time_str = round(time.time() * 1000)
sign = execjs.compile(js_code).call("get_sign",data1)
print(sign)

params = {
    '_': time_str,
    'sign': sign,
}

response = requests.post(url, headers = headers, cookies = cookies, params = params, data = data1.encode())
list = response.json()
item = list['req_1']['data']['body']['song']['list']
for s, li in enumerate(item):
    mids = li['mid']
    SongName = li['name']
    singername = li['singer'][0]['name']
    print(s + 1, SongName, singername)

songnum = input("输入下载歌曲的序号：")
mid = list['req_1']['data']['body']['song']['list'][int(songnum) - 1]['mid']
name = list['req_1']['data']['body']['song']['list'][int(songnum) - 1]['name']
print(mid)

urls = f'https://i.y.qq.com/v8/playsong.html?songmid={mid}&_qmp=3'
resp = requests.get(url=urls, headers=headers_mobile, cookies=cookies)
songurl = json.loads(re.findall('__ssrFirstPageData__\\s=(.*?)</script>', resp.text)[0])['songList'][0]['url']
print(songurl)

download = requests.get(url = songurl, headers=headers, cookies=cookies)
with open('./音乐文件/' + f'{name}.m4a', 'wb') as f:
    f.write(download.content)
    print(f'{name}下载完成')
# print(response)
