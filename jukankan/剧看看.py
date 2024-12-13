import requests
import json
import execjs
import re

print("请将浏览器中复制的cURL(Bash)内容粘贴到下面（按Enter两次结束输入）：")
curl_input = []
while True:
    line = input()
    if line == "":
        break
    curl_input.append(line)

curl_text = "\n".join(curl_input)

referer_match = re.search(r'-H\s*[\'"]Referer:\s*(https://jukankan\.cc/vplayer/index\.php\?vid=[^\'"]*)[\'"]', curl_text)
if referer_match:
    referer_url = referer_match.group(1)
    vid = referer_url.split('vid=')[1]
    print("获取到的vid:", vid)
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://jukankan.cc",
        "referer": referer_url,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "x-requested-with": "XMLHttpRequest"
    }

    url = "https://jukankan.cc/vplayer/api.php"
    data = {
        "vid": vid
    }

    response = requests.post(url, headers=headers, data=data)
    response_json = json.loads(response.text)
    encrypted_url = response_json['data']['url']
    print("提取的加密url值：", encrypted_url)

    with open("./js.js", 'r', encoding="utf-8") as f:
        js_code = f.read()

    real_url = execjs.compile(js_code).call("t", encrypted_url)
    print("解密后的真实url值：", real_url)
else:
    print("无法从cURL中找到Referer或vid参数")

    