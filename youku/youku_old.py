import re, requests, time, subprocess, json, base64
from hashlib import md5

class YouKu:
    def __init__(self, cookie):
        self.cookie = cookie

    def youku_sign(self, t, data, token):
        appKey = '24679788'     # 固定值
        '''token值在cookie中'''
        sign = token + '&' + t + '&' + appKey + '&' + data
        md = md5()
        md.update(sign.encode('UTF-8'))
        sign = md.hexdigest()
        return sign

    def utid(self):
        cna = re.compile("cna=(.*?);")
        _m_h5_tk = re.compile("_m_h5_tk=(.*?)_.*?;")
        token = _m_h5_tk.findall(self.cookie+";")
        utid_ = cna.findall(self.cookie+";")
        return {"utid": utid_[0], "token": token[0]}

    # 若直接在首页小窗口上复制的视频网址，是重定向的网址。
    def redirect(self, url):
        headers = {
            "referer": "https://www.youku.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }
        resp = requests.get(url=url, headers=headers)
        return resp.url

    def page_parser(self, url):
        headers = {
            "authority": "v.youku.com",
            "method": "GET",
            "path": url.replace("https://v.youku.com/",""),
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "cookie": self.cookie,
            "referer": "https://www.youku.com/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }
        resp = requests.get(url=url, headers=headers)
        html = resp.content.decode("utf-8")
        # print(html)
        videoId = re.compile("videoId: '(.*?)'")
        showid = re.compile("showid: '(.*?)'")
        currentEncodeVid = re.compile("currentEncodeVid: '(.*?)'")
        videoId = videoId.findall(html, re.S | re.M | re.I)
        current_showid = showid.findall(html, re.S | re.M | re.I)
        vid = currentEncodeVid.findall(html, re.S | re.M | re.I)
        return {"current_showid": current_showid[0], "videoId": videoId[0], "vid": vid[0]}

    def get_emb(self, videoId):
        emb = base64.b64encode(("%swww.youku.com/" % videoId).encode('utf-8')).decode('utf-8')
        return emb

    # 这个函数用来获取元素的第一个值
    def takeOne(self, elem):
        return float(elem[0])

    def m3u8_url(self, t, params_data, sign):
        url = "https://acs.youku.com/h5/mtop.youku.play.ups.appinfo.get/1.1/"

        params = {
            "jsv": "2.5.8",
            "appKey": "24679788",
            "t": t,
            "sign": sign,
            "api": "mtop.youku.play.ups.appinfo.get",
            "v": "1.1",
            "timeout": "20000",
            "YKPid": "20160317PLF000211",
            "YKLoginRequest": "true",
            "AntiFlood": "true",
            "AntiCreep": "true",
            "type": "jsonp",
            "dataType": "jsonp",
            "callback": "mtopjsonp1",
            "data": params_data,
        }

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": self.cookie,
            "Host": "acs.youku.com",
            "Referer": "https://v.youku.com/v_show/id_XNTA1MTYwMzU0OA==.html?spm=a2h0c.8166622.PhoneSokuUgc_3.dscreenshot",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }

        resp = requests.get(url=url, params=params, headers=headers)
        result =resp.text
        # print(result)
        data = json.loads(result[12:-1])
        # print(data)
        ret = data["ret"]
        video_lists = []
        if ret == ["SUCCESS::调用成功"]:
            stream = data["data"]["data"]["stream"]
            title = data["data"]["data"]["video"]["title"]
            print("解析成功:")
            for video in stream:
                m3u8_url = video["m3u8_url"]
                width = video["width"]
                height = video["height"]
                size = video["size"]
                size = '{:.1f}'.format(float(size) / 1048576)
                video_lists.append([size, width, height, title, m3u8_url])
                # print(f">>>  {title} 分辨率:{width}x{height} 视频大小:{size}M \tm3u8播放地址:{m3u8_url}")

            video_lists.sort(key=self.takeOne)
            for video_list in video_lists:
                print(f">>>  {title} 分辨率:{video_list[1]}x{video_list[2]} 视频大小:{video_list[0]}M \tm3u8播放地址:{video_list[4]}")
            self.play(video_lists[-1][4])    # 选择播放列表最后一个视频（经过sort排序后，最后一个即为清晰度最高的一个）
        elif ret == ["FAIL_SYS_ILLEGAL_ACCESS::非法请求"]:
            print("请求参数错误")
        elif ret == ["FAIL_SYS_TOKEN_EXOIRED::令牌过期"]:
            print("Cookie过期")
        else:
            print(ret[0])


    def play(self, x):
        text = 'ffplay -protocol_whitelist "file,http,https,rtp,udp,tcp,tls" -loglevel quiet -i "%s"' % x
        subprocess.call(text, shell=True)

    def start(self):
        while True:
            try:
                t = str(int(time.time() * 1000))
                user_info = self.utid()
                userid = user_info["utid"]
                url = input("\n\n请将优酷视频播放链接粘贴到这:\n")
                url = self.redirect(url)
                page_info = self.page_parser(url)
                emb = self.get_emb(page_info["videoId"])
                params_data = r'''{"steal_params":"{\"ccode\":\"0502\",\"client_ip\":\"192.168.1.1\",\"utid\":\"%s\",\"client_ts\":%s,\"version\":\"2.1.69\",\"ckey\":\"DIl58SLFxFNndSV1GFNnMQVYkx1PP5tKe1siZu/86PR1u/Wh1Ptd+WOZsHHWxysSfAOhNJpdVWsdVJNsfJ8Sxd8WKVvNfAS8aS8fAOzYARzPyPc3JvtnPHjTdKfESTdnuTW6ZPvk2pNDh4uFzotgdMEFkzQ5wZVXl2Pf1/Y6hLK0OnCNxBj3+nb0v72gZ6b0td+WOZsHHWxysSo/0y9D2K42SaB8Y/+aD2K42SaB8Y/+ahU+WOZsHcrxysooUeND\"}","biz_params":"{\"vid\":\"%s\",\"play_ability\":16782592,\"current_showid\":\"%s\",\"preferClarity\":99,\"extag\":\"EXT-X-PRIVINF\",\"master_m3u8\":1,\"media_type\":\"standard,subtitle\",\"app_ver\":\"2.1.69\",\"h265\":1}","ad_params":"{\"vs\":\"1.0\",\"pver\":\"2.1.69\",\"sver\":\"2.0\",\"site\":1,\"aw\":\"w\",\"fu\":0,\"d\":\"0\",\"bt\":\"pc\",\"os\":\"win\",\"osv\":\"10\",\"dq\":\"auto\",\"atm\":\"\",\"partnerid\":\"null\",\"wintype\":\"interior\",\"isvert\":0,\"vip\":1,\"emb\":\"%s\",\"p\":1,\"rst\":\"mp4\",\"needbf\":2,\"avs\":\"1.0\"}"}'''% (userid, t[:10], page_info["vid"], page_info["current_showid"], emb)
                sign = self.youku_sign(t, params_data, user_info["token"])
                self.m3u8_url(t, params_data, sign)
            except Exception as e:
                print('error:',e , "或可能cookie设置错误")
                break

if __name__ == '__main__':
    print("="*35 +'>> 欢迎使用优酷视频m3u8地址解析工具 <<'+"="*35)
    cookie = input("\n使用前,请设置优酷的cookie:\n")
    print("\n这是一个循环：可以不停的解析...")
    youku = YouKu(cookie)
    youku.start()
