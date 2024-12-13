import requests, subprocess
import time
import execjs
import json
import re
from urllib.parse import urlparse, parse_qs
import urllib.parse

cookie = ''
headers = {
    "^Accept": "*/*^",
    "^Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^",
    "^Cache-Control": "no-cache^",
    "^Connection": "keep-alive^",
    "^Origin": "https://www.iqiyi.com^",
    "^Pragma": "no-cache^",
    "^Referer": "https://www.iqiyi.com/^",
    "^Sec-Fetch-Dest": "script^",
    "^Sec-Fetch-Mode": "no-cors^",
    "^Sec-Fetch-Site": "same-site^",
    "^User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0^",
    "^sec-ch-ua": "^\\^Microsoft",
    "^sec-ch-ua-mobile": "?0^",
    "^sec-ch-ua-platform": "^\\^Windows^^^",
    "^accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8^",
    "^accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^",
    "^cache-control": "no-cache^",
    "^pragma": "no-cache^",
    "^priority": "i^",
    "^referer": "https://www.iqiyi.com/^",
    "^sec-fetch-dest": "image^",
    "^sec-fetch-mode": "no-cors^",
    "^sec-fetch-site": "cross-site^",
    "^user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0^",
    "^cookie": cookie,
  #  "^Cookie": "QC006=m9n2hiucaxykt1n8obwn2gv4; P00004=.1729579314.cbbc5e3a41; P00010=1683451979; P01010=1730044800; P00007=c82pOdaEIm2rRlEVBueGRMIZUIxeSwvUQl0NJDRm1GxhrkSif2Dk7hMb13m2opHpfe5TP7c; P00PRU=1683451979; QC005=b0f3d36f9ca820ea7d76810d654d57ab; QC234=10b92987a61c395de65dcd3cbe0d4f02; QC235=320634e1af6c473cba71843a393cf752; PD005=xg60zcjpxe10825jedw1o29nzp7jg526; QP0034=^%^7B^%^22v^%^22^%^3A17^%^2C^%^22dp^%^22^%^3A1^%^2C^%^22dm^%^22^%^3A^%^7B^%^22wv^%^22^%^3A1^%^7D^%^2C^%^22m^%^22^%^3A^%^7B^%^22wm-vp9^%^22^%^3A1^%^2C^%^22wm-av1^%^22^%^3A1^%^7D^%^2C^%^22hvc^%^22^%^3Atrue^%^7D; T00404=ab8f9832d46254e269dbe25e968951f3; QC007=https^%^3A^%^2F^%^2Fcn.bing.com^%^2F; T00700=EgcI9L-tIRABEgcI58DtIRABEgcIrcHtIRABEgcI8L-tIRABEgcIz7-tIRABEgcI67-tIRABEgcIkMDtIRABEgcIg8DtIRABEgcI0b-tIRABEgcI4b-tIRABEgcIhcDtIRABEgcIi8HtIRABEgcI87-tIRABEgcI7L-tIRABEgcImMDtIRABEgcI57-tIRAB; QP0025=1; __dfp=a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f^@1734490139879^@1733194140879; QP0027=26; curDeviceState=width^%^3D604^%^3BconduitId^%^3D^%^3Bscale^%^3D120^%^3Bbrightness^%^3Ddark^%^3BisLowPerformPC^%^3D0^%^3Bos^%^3Dbrowser^%^3Bosv^%^3D10.0.19044; QP0037=45; QP0033=1; QP0035=2; IMS=IggQARj_m8e6Bio1CiBiODE2NWRiZTkwNjMzYTk1ZGI2OWZjNjQzYTllYmEyYRABGKwCIggI0AUQAhiwCShJMAUwADAAMAByJAogYjgxNjVkYmU5MDYzM2E5NWRiNjlmYzY0M2E5ZWJhMmEQAIIBBCICEAKKASgKJgokMjBmMGEzNmItYzc2MC00ZTYyLWEzYWYtNzhmMjlkNjg1YzNm; QP007=13165260; QP0036=2024125^%^7C287.898^",
    "^Referer;^": "",
    "^content-type": "application/x-www-form-urlencoded^",
    "^origin": "https://www.iqiyi.com^",
    "^access-control-request-headers": "content-type^",
    "^access-control-request-method": "POST^"
}
def play(file_path):
    text = f'ffplay -protocol_whitelist "file,http,https,rtp,udp,tcp,tls" -loglevel quiet -i "{file_path}"'
    try:
        subprocess.call(text, shell=True)
    except FileNotFoundError:
        print("Error: ffplay is not installed or not in PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
def m3u8_down(title, text):
    with open(f"m3u8_down\\{title}.m3u8", "w") as f:
        f.write(text)

def get_tvid(tvurl):
    accelerator = "https://mesh.if.iqiyi.com/player/lw/lwplay/accelerator.js"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36¬"
    }
    headers["Referer"] = tvurl.split("?")[0]
    res = requests.get(accelerator, headers=headers)
    res.encoding = 'utf-8'
    tvid = re.search('"tvid":([A-Za-z0-9]+)', res.text)
    vid = re.search('"vid":"([A-Za-z0-9]+)"', res.text)
    tl = re.search(r'"tl":"([^"]+)"', res.text)
    return {
            "tvid": tvid.group(1), 
            "vid": vid.group(1), 
            "tl": tl.group(1)
        }

with open("js.js", 'r', encoding="utf-8")as f:
    js_code = f.read()

tm = str(int(time.time() * 1000))
tvurl = input("输入视频链接：")
# parsed_url = urlparse(tvurl)
# query_params  = parse_qs(parsed_url.query)
# if 'tvname' in query_params:
#     title = urllib.parse.unquote(query_params['tvname'][0])
# else:
#     title = input("未能自动获取名称，请手动输入影视剧名字：")
# print(title)

# vid = urllib.parse.unquote(query_params['vid'][0])
pageinfo = get_tvid(tvurl)

print('tvid:', pageinfo['tvid'])
print('vid:', pageinfo['vid'])
print('tl:', pageinfo['tl'])

tvid = pageinfo['tvid']
vid = pageinfo['vid']
tl = pageinfo['tl']

pck = re.findall("P00001=(.*?);", cookie)[0]
print("pck的值：",pck)

text = "d41d8cd98f00b204e9800998ecf8427e" + tm + tvid

authkey = execjs.compile(js_code).call("key", text)
print('authkey:', authkey)

r = f"/dash?tvid={tvid}&bid=500&vid={vid}&src=01010031010000000000&vt=0&rs=1&uid=1683451979&ori=pcw&ps=1&k_uid=b0f3d36f9ca820ea7d76810d654d57ab&pt=0&d=0&s=&lid=0&cf=0&ct=0&authKey={authkey}&k_tag=1&dfp=a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f&locale=zh_cn&pck={pck}&up=&sr=1&cpt=0&qd_v=a1&tm={tm}&k_ft1=706436220846084&k_ft4=1161221786574852&k_ft5=137573171201&k_ft7=4&fr_1020=120_120_120_120_120_120&fr_800=120_120_120_120_120_120&fr_600=120_120_120_120_120_120&fr_500=120_120_120_120_120_120&fr_300=120_120_120_120_120_120&bop=%7B%22version%22%3A%2210.0%22%2C%22dfp%22%3A%22a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f%22%2C%22b_ft1%22%3A24%7D&ut=0"

# js_executor = execjs.compile(js_code)
# vf = js_executor.call("key", js_executor.call("dash", r))
i = execjs.compile(js_code).call("dash", r)
vf = execjs.compile(js_code).call("key", i)

print('vf:', vf)

url = "https://cache.video.iqiyi.com/dash"
params= {
    "tvid": tvid,
    "bid": "500",  # 清晰度 500是730p，300是360，600是1080p，这儿变上面r也要变
    "vid": vid,
    "src": "01010031010000000000",
    "vt": "0",
    "rs": "1",
    "uid": "1683451979", # 不登陆是空，这儿变上面的r也要变
    "ori": "pcw",
    "ps": "1",
    "k_uid": "b0f3d36f9ca820ea7d76810d654d57ab",
    "pt": "0",
    "d": "0",
    "s": "",
    "lid": "0",
    "cf": "0",
    "ct": "0",
    "authKey": authkey,
    "k_tag": "1",
    "dfp": "a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f",
    "locale": "zh_cn",
    "pck": pck,
    "up": "",
    "sr": "1",
    "cpt": "0",
    "qd_v": "a1",
    "tm": tm,
    "k_ft1": "706436220846084",
    "k_ft4": "1161221786574852",
    "k_ft5": "137573171201",
    "k_ft7": "4",
    "fr_1020": "120_120_120_120_120_120",
    "fr_800": "120_120_120_120_120_120",
    "fr_600": "120_120_120_120_120_120",
    "fr_500": "120_120_120_120_120_120",
    "fr_300": "120_120_120_120_120_120",
    "bop": "{\"version\":\"10.0\",\"dfp\":\"a011c8795c0024477ebc1ffc0417755363a0c8620d7d68afa8ab27aa59174b8d3f\",\"b_ft1\":24}",
    "ut": "0", # vip是1，非vip是0， 这儿变上面的r也要变
    "vf": vf
}
response = requests.get(url, headers=headers, params=params)
print(response)

data = json.loads(response.content.decode("utf-8"))
# print(data)

video = data['data']['program']['video']
video_m3u8 = []
for v in video:
    if v.get("m3u8"):
        m3u8 = v["m3u8"]  
        scrsz = v["scrsz"]  
        vsize = v["vsize"]  
        v_url = re.compile("(http://.*?)#", re.S | re.M | re.I)
        video_url = v_url.findall(m3u8)[-1] 
        start = re.compile("(start=.*?)&")
        start = start.findall(video_url)[0]
        video_url = video_url.replace(start, "start=0")
        vsize = '{:.1f}'.format(float(vsize) / 1048576)
        video_m3u8.append({"video_url": video_url, "m3u8": m3u8, "scrsz": scrsz, "vsize": vsize})
try:
    for video in video_m3u8:
        video_url = video["video_url"]
        m3u8 = video["m3u8"]
        scrsz = video["scrsz"]
        vsize = video["vsize"]
        name = f"{tl}_分辨率-{scrsz}-视频大小-{vsize}M"
        m3u8_down(name, m3u8)
        print(f"{name}.m3u8 文件缓存完成。 保存在m3u8_down文件夹中")
        print("解析成功 >>>  标题：{0}\t 分辨率：{1} 视频大小：{2}M \tm3u8播放地址：{3}".format(tl, scrsz, vsize, video_url))
        file_path = "./m3u8_down/" + name + ".m3u8"
        play(file_path)
except Exception as e:
    print('error:', e)