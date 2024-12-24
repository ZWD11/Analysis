import requests, json, execjs

keyword = str(input("输入搜索内容："))

with open('./xs.js', 'r', encoding='utf-8')as f:
    js_code = f.read()
search_id = execjs.compile(js_code).call('l')

with open('./xs-common.js', 'r', encoding='utf-8')as f:
    js_code1 = f.read()
x_b3_traceid = execjs.compile(js_code1).call('get_trace_id')
xs_t_common = execjs.compile(js_code1).call('get_xs_t_common',search_id,keyword)
x_common = xs_t_common['x_common']
x_s_t = xs_t_common['x_s_t']

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "access-control-request-headers": "content-type,x-b3-traceid,x-s,x-s-common,x-t,x-xray-traceid",
    "access-control-request-method": "POST",
    "cache-control": "no-cache",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-b3-traceid": x_b3_traceid,
    "x-s": x_s_t["X-s"],
    "x-s-common": x_common,
    "x-t": str(x_s_t["X-t"]),
    "x-xray-traceid": "c91c" # 补充完整
}
cookies = {  # 需补充cookie，连同xs.js和xs-common里面的部分也需要补充，看注释补
    "abRequestId": "b58a8",
    "a1": "193e",
    "webId": "31254",
    "gid": "yjq4",
    "xsecappid": "xhs-pc-web",
    "web_session": "04006a6",
    "webBuild": "4.48.0",
    "acw_tc": "0a5f369e",
    "websectiga": "2840d",
    "sec_poison_id": "2608255",
    "unread": "{%22ub:34}"
}
url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
data = {"keyword":keyword,"page":1,"page_size":20,"search_id":search_id,"sort":"general","note_type":0,"ext_flags":[],"image_formats":["jpg","webp","avif"]}
data = json.dumps(data, separators=(',', ':'),ensure_ascii=False).encode("utf-8")
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)