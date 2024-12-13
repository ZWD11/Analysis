import time, base64, re, json, requests, subprocess
from hashlib import md5

class YouKu:
    def __init__(self, cookie, url=None):
        if url is None:
            self.url = input("请输入优酷视频链接: ")
        else:
            self.url = url
        self.int_time = int(time.time()) * 1000 
        self.cookie = cookie
        self.video_url = self.url
        self.page_info = self.page_parser(self.video_url)
        self.params = {}
        self.language = {
            "ja": "日语",
            "guoyu": "国语",
            "default": "默认",
            "yue": "粤语",
        }

    def get_steal_params(self):
        return json.dumps({
            "ccode": "0502",
            "utid":  re.findall("cna=(.*?);", self.cookie)[0],
            "version": "9.5.17",
            "ckey": "140#Y2MdoI6czzWnJQo22iRuA6Sdv7J1YkRgmJDKuAtZT/dNufUYvr57hd68zKUFaYZZQJa21oGY1s+A7//iUGHz4P+mB3hqzzcDye6HozMzzjPbIHoulFzx2DD3VthqzFPY25uuXvVsVPFiIXJqlaOz2PD+VKfr/uBPxrvZrI7ZbYNw4p301L5UaGfJu2wEkBJ9UaO/pn5/gZPbEZW/W6OyT/s8ZZlC0MXLA/52KOV4vWMnd+VchB5Fwh3jpDjho9I3tqUjmHj+EYvks1VmlAcQx2w4dZqxW2k4LE6aYjWq8E6HgAk53Vx+sNCvPwsyQnOx4AlALjsFvggN7MptgT6Fy23zPRnwiJlEabmJReoauvaaWXPAzdWBhXRFNpDrxXHb/xIgnxVWesXAMFxdZNgblhDYupWnIzGCU85sqs+7k3WHEJ9ePCk8c7F8Ii2rHh2zQDMbdSYuNaSzWIdR5jw0SpHoIkQSC9mQ5k1Jkb7qxy8WNR4d9tamCrTDDbjzr176sOfVyojD1trIU5Apl9Yw4emNxuarc9ltWHVXPkFIm33uZvMEZHlQhkP2D1lfy6hSy/5+hzwrJngW151ZoHGObAr143LYZzaTcXcQySPCYWGgDwNJCIHz/PBLuGvKX2VLRKhzQ1S4CHiTEW4+sKe3dEBWnpgP1qrofZQjCtCj+wMsJTUpFFZnZj/IXdcXZRGtP/VkaHbkxj9jXCoXLPj5AQd1NXwEW+6A/GNAJjmK8TKVPOScNN2Z2mEgPqmFAtiN9FYtAYiP1MuCBppe8cSmwsIuYn6iU5TTUfsInyCXCjA6IDJb6rzVtoDsZZdYDfqRPUY8gSuYvCxA76fK04JEW6N9wskEM66MQyfURkFgrmF0GyE6eVH7Z4TU6RspiqPnXY8Ap0N7EJeYQh1rUHPN3rzawhZyn9z68KB2Rshyd59c0NEectJvIv2GMuTZzgoqwkE3qTByXEMmfl1Al71qrLBKxXYo4hwzPgmyN/eSUoE+JHRILiLk8sFysISHkG+/sjhZl0wI8KDz2Jtf45KEMyZEbfLfuhppp/jiW7qMMUzUQCutn7dQHJ5mv4FTr3m0ZxGOs8ZAvFjrpCb6H9SYxbeLujQO/4dSzgb/8Of06MFwUrbZHCdOCjVIoOZheg+SHLt6uWj8s+OHVllh2W4nsjR6JpsEFnQMZGBkNYNF72xER8G2I73f7LjSqOW+8XRfwzcr1Y4129PiYMtXyb2TC/3vlvzM2jJT0zBCgqKTakZEo5M24RiXUA5dWpM9fmpEbXIPJBLP9k81lcPPbSR6LgOrgmkhFTHVqGbFnntV+ssD1+RR8mDGd8TO56NlEHVVuX1mrvMo4k68ZVbwsFb6YzMQYMo3jFnh1ZX4gJAow0A0V3+VhunrhgxGIiiWBrNB85ABFk/6C8VoQt/zYvksGFobXsRi5KNhdFQN/UWpDsZAXho4Kvp4hIkuKRxaQUVcFSqR1+klRhTXTWt2pdlgmZtzLXGlv5zcAkJof1Hooxd2Xcch7XDOQ8MwvpfP26B/NAePLNqhXMjSPdodgCpEixX8GBLo0Ep7oB67O5zu/69fdliOuPZNxMvswVT8F1Qi5haAIiA9TK3JQKFGJHuhT5NrF51+cJywh51VAzGfyA4swlFO3XwHOCVXKMvbB87d1Z0ShOOf8VMcx8l4AQd20tEsvtXch+5jBl6RxUGIAnBtgbTHxrz6l+yvje6KhzuG0ZYYgdenuF==",
            "client_ip": "192.168.1.1",
            "client_ts": self.int_time
        })

    def get_biz_params(self):
        return json.dumps({
            "vid": self.page_info['vid'],
            "h265": 0,
            "current_showid": self.page_info['current_showid'],
            "preferClarity": 99,
            "media_type": "standard,subtitle",
            "app_ver": "9.5.17",
            "extag": "EXT-X-PRIVINF",
            "play_ability": 16782592,
            "master_m3u8": 1,
            "drm_type": 19,
            "key_index": "web01",
            "encryptR_client": "s1Hf00lfTdfyidWQEicILQ==",
            "local_vid": self.page_info['vid'],
            "local_time": self.int_time,
            "skh": 1,
            "start_point_ms": 90850,
            "last_clarity": 2,
            "clarity_chg_ts": self.int_time
        })

    def get_ad_params(self):
        return json.dumps({
            "vs": "1.0",
            "pver": "9.5.17",
            "sver": "2.0",
            "site": 1,
            "aw": "w",
            "fu": 0,
            "d": "0",
            "bt": "pc",
            "os": "win",
            "osv": "10",
            "dq": "hd2",
            "atm": "",
            "partnerid": "null",
            "wintype": "interior",
            "isvert": 0,
            "vip": 0,
            "emb": "",
            "p": 1,
            "rst": "mp4",
            "needbf": 2,
            "avs": "1.0"
        })

    def get_data(self):
        return json.dumps({"steal_params": self.get_steal_params(), "biz_params": self.get_biz_params(),
                           "ad_params": self.get_ad_params()})

    def join_params(self):
        data = self.get_data()
        return {
            'jsv': '2.6.1',
            'appKey': '24679788',
            't': self.int_time,
            'sign': md5(str(
                re.findall("m_h5_tk=(.*?)_", self.cookie)[0] + "&" + str(self.int_time) + "&" + "24679788" + "&" + str(
                    data)).encode("utf8")).hexdigest(),
            'api': 'mtop.youku.play.ups.appinfo.get',
            'v': '1.1',
            'timeout': '15000',
            'AntiFlood': 'true',
            'AntiCreep': 'true',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp1',
            "data": f"{data}"
        }
    
    def parse_jsonp(self, jsonp_str):
        match = re.search(r'\((.*)\);?$', jsonp_str)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        return None
    
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
    
    def takeOne(self, elem):
        return float(elem[0])
    
    def play(self, x):
        text = 'ffplay -protocol_whitelist "file,http,https,rtp,udp,tcp,tls" -loglevel quiet -i "%s"' % x
        subprocess.call(text, shell=True)

    def start(self):
        headers = {
            "^Accept": "*/*^",
            "^Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6^",
            "^Cache-Control": "no-cache^",
            "^Connection": "keep-alive^",
            "Host": "acs.youku.com",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "cookie": self.cookie,
            "Referer": "https://v.youku.com/v_show/id_XNjQ1MDE1NzY0MA==.html?spm=a2hja.14919748_WEBTV_JINGXUAN.drawer4.d_zj1_2",
        }
        res = requests.get("https://un-acs.youku.com/h5/mtop.youku.play.ups.appinfo.get/1.1/", params=self.join_params(), headers=headers)
        data = self.parse_jsonp(res.content.decode("utf-8"))
        # data = res.text
        #print(data)
        ret = data['ret']
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
                video_lists.append([ width, height, size, title, m3u8_url])

            video_lists.sort(key=self.takeOne)
            for video_list in video_lists:
                print(f">>>  {title} 分辨率:{video_list[1]}x{video_list[2]} 视频大小:{video_list[0]}M \tm3u8播放地址:{video_list[4]}")
            self.play(video_lists[-1][4])
        elif ret == ["FAIL_SYS_ILLEGAL_ACCESS::非法请求"]:
            print("请求参数错误")
        elif ret == ["FAIL_SYS_TOKEN_EXOIRED::令牌过期"]:
            print("Cookie过期")
        else:
            print(ret[0])

if __name__ == '__main__':
    cookie = 'isI18n=false; cna=WuHbH3Xd6RICAduS/vFiWtL3; __ysuid=1733620571527RT8; __aysid=1733620571528MBE; P_gck=NA%7CpatUEOBtZYnKW2WsVpG4LQ%3D%3D%7CNA%7C1733621854089; P_pck_rm=cJEa8Yh550b3ad167076f3ZB7W73NeSRiRz6cw68oZgkW14fw%2FDPWEXCqBtYdILOpgRxKJm%2FeoqHs8NISggnlto6%2BjVSW8n5kEfacJ1QHouEq1LWC2z4gJvmXxo%2BDPh9evtSy%2BoqPlaAYlbcFZ0%2FnFWTTDjwFpIaOACelNSN2fRXpM2V63fLb9%2FjcxI%3D%5FV2; disrd=90594; webpushRejected=1; 32841-index=1; 32841-startTime=1733800700487; isg=BHh4kJTqa4xVW4cLmpkcyMoQSSYK4dxrIRhGvbLprbNmzRm3WvMj-i2sgcX9nZRD; xlly_s=1; csrfToken=n2XTdhbWmekW7nKAq5tQabbH; __ayft=1734018648887; __arpvid=1734018648887SMlSxJ-1734018648911; __ayscnt=1; __aypstp=1; __ayspstp=86; _m_h5_tk=1068a41094f4f021210f8983e0019b61_1734022790963; _m_h5_tk_enc=bb0765c6024c22d1ade9d63715c447ed; vip_auto_hover_index=1_1734018652971; __ayvstp=1; __aysvstp=1; tfstk=g1LjOn4Fc-2b4c2kixhPF8dwT7_1GdgF1519tCU46ZQYBRddUSWVgKz9Vdpl0tL6sP196dccQjmyiIbGWvke52RDiYqyucMPWfdR711GNA-BiIbGW7ytY3d0CnQEjIQ9BaIRO6_TBiItNaCc6NUAXrE8eTfOWNIAM7FR_6rA61p9wb1GeOQODbGqF_mfHIGyi-m7-mbBMTaTWEgGc9OLbPU9PssfAIBW0n85Gi6dqI1MnEpy6E8cq0E5SQ-BChpKUoWvA695YnMQlp9c6C19h2VCeEO6PixzTyO5fttJkgNTWQRRBp-6hxZcHnJ5x_I812fyLTdDk3GgeIpFhZCR42hBwGKyoMYqer_pxI72XpHz0tKC6gRz89GzYlN5xP15LbG7jlbHQrAdt04NniClaelSN-ZGD_f5LbG7jljAZ_SENbwbj'
    youku = YouKu(cookie)  
    youku.start()