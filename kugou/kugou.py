import requests
import time
import execjs
import hashlib
import json

name = input("请输入搜索内容：")

cookies = {
    "kg_mid": "d6208993432d095924116ff0bed6913a",
    "kg_dfid": "1bmGAb3i4Nmc0pt8xL2Vzl5v",
    "ACK_SERVER_10017": "%7B%22list%22%3A%5B%5B%22gzverifycode.service.kugou.com%22%5D%5D%7D",
    "ACK_SERVER_10015": "%7B%22list%22%3A%5B%5B%22gzlogin-user.kugou.com%22%5D%5D%7D",
    "ACK_SERVER_10016": "%7B%22list%22%3A%5B%5B%22gzreg-user.kugou.com%22%5D%5D%7D",
    "kg_dfid_collect": "d41d8cd98f00b204e9800998ecf8427e",
    "kg_mid_temp": "d6208993432d095924116ff0bed6913a",
    "KuGooRandom": "66531734014486089"
}
headers = {
    "^accept": "*/*^",
    "^accept-language": "zh-CN,zh;q=0.9^",
    "^cache-control": "max-age=0^",
    "^cookie": "kg_mid=8f3d9da03ed8b2ea3f4be3d80a1a0fb9; kg_dfid=0R6i2k36fjNa2M82Ex4dK1op; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e^",
    "^if-modified-since": "Thu, 18 Nov 2021 05:03:36 GMT^",
    "^if-none-match": "^\\^6195dea8-577e^^^",
    "^priority": "u=1, i^",
    "^referer": "https://www.kugou.com/^",
    "^sec-ch-ua": "^\\^Chromium^^;v=^\\^130^^, ^\\^Microsoft",
    "^sec-ch-ua-mobile": "?0^",
    "^sec-ch-ua-platform": "^\\^Windows^^^",
    "^sec-fetch-dest": "script^",
    "^sec-fetch-mode": "no-cors^",
    "^sec-fetch-site": "same-site^",
    "^sec-fetch-user": "?1^",
    "^upgrade-insecure-requests": "1^",
    "^user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0^",
    "^origin": "https://www.kugou.com^",
    "^Referer": "https://www.kugou.com/^",
    "^User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0^",
    "^Accept": "*/*^",
    "^Accept-Language": "zh-CN,zh;q=0.9^",
    "^Connection": "keep-alive^",
    #"^Cookie": "kg_mid=d6208993432d095924116ff0bed6913a; kg_dfid=1bmGAb3i4Nmc0pt8xL2Vzl5v; ACK_SERVER_10017=%7B%22list%22%3A%5B%5B%22gzverifycode.service.kugou.com%22%5D%5D%7D; ACK_SERVER_10015=%7B%22list%22%3A%5B%5B%22gzlogin-user.kugou.com%22%5D%5D%7D; ACK_SERVER_10016=%7B%22list%22%3A%5B%5B%22gzreg-user.kugou.com%22%5D%5D%7D; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; kg_mid_temp=d6208993432d095924116ff0bed6913a; KuGooRandom=66531734014486089",
    "^If-Modified-Since": "Mon, 19 Jun 2023 07:59:22 GMT^",
    "^If-None-Match": "^\\^64900ada-1976^^^",
    "^Sec-Fetch-Dest": "script^",
    "^Sec-Fetch-Mode": "no-cors^",
    "^Sec-Fetch-Site": "same-site^",
    "^content-type": "application/x-www-form-urlencoded^"
}
time_str = round(time.time() * 1000)
s = [
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
    "appid=1014",
    "bitrate=0",
    "callback=callback123",
    "clienttime={}".format(time_str),
    "clientver=1000",
    "dfid={}".format(cookies['kg_dfid']),
    "filter=10",
    "inputtype=0",
    "iscorrection=1",
    "isfuzzy=0",
    "keyword={}".format(name),
    "mid={}".format(cookies['kg_mid']),
    "page=1",
    "pagesize=30",
    "platform=WebFilter",
    "privilege_filter=0",
    "srcappid=2919",
    "token=",
    "userid=0",
    "uuid={}".format(cookies['kg_mid']),
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
]
t = "".join(s)
with open("./sign.js", 'r', encoding="utf-8")as f:
    js_code = f.read()

# sign = hashlib.md5(t.encode()).hexdigest()
sign = execjs.compile(js_code).call("md5",t)
print(sign)

url = "https://complexsearch.kugou.com/v2/search/song"
params = {
    "srcappid": "2919",
    "clientver": 1000,
    "clienttime": time_str,
    "mid": cookies['kg_mid'],
    "uuid": cookies['kg_mid'],
    "dfid": cookies['kg_dfid'],
    "keyword": name,
    "page": 1,
    "pagesize": 30,
    "bitrate": 0,
    "isfuzzy": 0,
    "inputtype": 0,
    "platform": "WebFilter",
    "userid": "0",
    "iscorrection": 1,
    "privilege_filter": 0,
    "callback": "callback123",
    "filter": 10,
    "token": "",
    "appid": 1014,
    "signature": sign
}

list = json.loads(requests.get(url=url, headers=headers, params=params, cookies=cookies).text[12:-2])
item = list['data']['lists']
for s, li in enumerate(item):
    ids = li['EMixSongID']
    SongName = li['SongName']
    singername = li['SingerName']
    print(s + 1, SongName, singername)

songnum = input("下载哪一首：")
ID = list['data']['lists'][int(songnum) - 1]['EMixSongID']
name = list['data']['lists'][int(songnum) - 1]['SongName']
print(ID)

besigninfo = [
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
    "appid=1014",
    "clienttime={}".format(time_str),
    "clientver=20000",
    "dfid={}".format(cookies['kg_dfid']),
    "encode_album_audio_id={}".format(ID),
    "mid={}".format(cookies['kg_mid']),
    "platid=4",
    "srcappid=2919",
    "token=",
    "userid=0",
    "uuid={}".format(cookies['kg_mid']),
    "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
]

p = "".join(besigninfo)

signature = execjs.compile(js_code).call("md5",p)
# print(signature)

spa = {
    "srcappid": "2919",
    "clientver": "20000",
    "clienttime": time_str,
    "mid": cookies['kg_mid'],
    "uuid": cookies['kg_mid'],
    "dfid": cookies['kg_dfid'],
    "appid": 1014,
    "platid": 4,
    "encode_album_audio_id": ID,
    "token": "",
    "userid": "0",
    "signature": signature
}

urls = "https://wwwapi.kugou.com/play/songinfo"

song = requests.get(url=urls, headers=headers, params=spa, cookies=cookies).json()
# print(song)
songurl = song['data']['play_url']
dowmload = requests.get(url=songurl,headers=headers).content
with open('音乐文件/' + f'{name}.mp3', 'wb')as ds:
    ds.write(dowmload)
    print(songurl)
    print(f'{name}下载完成')

# print(response.text)
# print(response)