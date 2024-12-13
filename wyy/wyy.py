import requests
import execjs
import json

search = input("请输入搜索内容：")
cookies = {
    "NMTID": "00OqmKm6FcoSXGBBUpCoLBs6gDaer0AAAGQ4mpMVA",
    "_ntes_nnid": "d6ebdc0745db6aeba53a6cfd09990db6,1721785632190",
    "_ntes_nuid": "d6ebdc0745db6aeba53a6cfd09990db6",
    "sDeviceId": "YD-Zo7EAQe3wIBEF1FRQBOA%2FvC9FzCW8sQs",
    "__snaker__id": "xccyLbf4lbZhJKCH",
    "ntes_kaola_ad": "1",
    "_iuqxldmzr_": "32",
    "WM_TID": "oDuLELfkEYRBUAAAAUKWXf4nu%2BV9AmzG",
    "ntes_utid": "tid._.FpnQ007qyjhAV1BREFKGXb9mqqU%252FCSv5._.0",
    "JSESSIONID-WYYY": "gTOt%2B%2FD0Wpb1v87PIwKreunq9w%5CvU2UBVJGNJByf966UU%2F9IfJi9jk1%2F5mNk5vONdqXjijS0%2FhzQiFwCVXJjZKB0mqPjganRZ7Q2rep5ImzfP0t%2B0tK7foQ%5Ct9V2w1nsYf2mmrMJ8EDKDrw5m1%2BkKphNKCiW5%2FpSoWXj%2BwrStfaBFU4j%3A1734017533893",
    "__csrf": "731f6011d7617294602cda98f07e91ce",
    "MUSIC_U": "0024B15E8B86010E0AF0623CA2E619AD234022E2C836EC00923B0D4E89184D9F7936FAC8CE7CE807263CCE56B4BCF82AC01CD547B77F10F8FD1EE2ACF335FB330B602B772917FE0C0EE6C7AB0AD2A2AD3DD198CB0E6617BC3D929C95418B980757492B0AA44629728BF34F65CA471459D5DF76FBDF18DD8B3164935AC15749E77BD2AE8BF7FB4EA4DB23E073CB4816D7CFD5FCDE0F7E7483828964AE455C82561D56D6E5CAF716EBE6C8420C9395739E3692296EC9B9AD97BF2F155B5B45BD89CFE7D95751AD960742BCFE729A35853F445D1A99277B18D82D03C54B0D32D717CA9DE2F936A2A24397E312EA2D2CAD7569FDCE01DECA170024C3108C4EDFF3968EC7DC6137F4E1DE1BD08A3C03EFC1C4B912196FD86E6DA2DFAA8F643B87CFF43337442D3C9070B9FB53B3BCBD41D51F9F0B6EE6596562EAC1708B346B8D0C4BCC7C815D31992D5769D1424A90414F417987C5BBCD9DCA2935B0837BE833B384E542F7D73CEF36CCCFA5C9043460A8FF2E"
}
headers = {
    "^accept": "*/*^",
    "^accept-language": "zh-CN,zh;q=0.9^",
    "^content-type": "application/x-www-form-urlencoded^",
    #"^cookie": "NMTID=00OsFHmt1dpCFNBJEYhmNDqDcnujL0AAAGTdcH4EA; _iuqxldmzr_=32; _ntes_nnid=2c51e69ab9b7c1643df7b8f7281a22be,1732847468200; _ntes_nuid=2c51e69ab9b7c1643df7b8f7281a22be; WEVNSM=1.0.0; WNMCID=lvghoe.1732847468742.01.0; WM_NI=pKPQruP5Kpp9ozDX2SPbsNrkP^%^2Fqq^%^2BEOrFi15h^%^2Fr1CLP^%^2FUSdyqEtjRK3D2gi4ZtcQs65bJtO2M1f7LvvwPZEvAQEvP^%^2FSFMBDTcIIRnqXwp2tU9qG2WLB665WTmC0YChr5WWU^%^3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb3b16b90979a96d2408b868fb6d44b978f8bb1cb44f1b1a2d5d46896aeacccf42af0fea7c3b92ab495a0b2f17f94eb8591f333ada68cb9b15994bebdaff16194f1bf92aa4f8dae8a8ab43facf1bed2c24894f19bb4e773b39bbc8bd141f19cfe88ec409aacadb2f23ef7be8695ce3a8fefaad8cf7eb6a9a0bbc87e838f8b97d325919a83a3c760a19787b3ed7b9ca9c0d3f75ffbaf89d3d64882eafad6d660af9d00bac264b2eb99b8d837e2a3; WM_TID=zrNJ1WSd3S5EAFAUBALGXipm8UlV^%^2FZu^%^2B; ntes_utid=tid._.^%^252BA3TfMKQgphFElAVUFKSDmsi8AhSkfeH._.0; sDeviceId=YD-QdwvosyE9ShBFhRUFRKGCn4m8Q1DxPKM; __snaker__id=MLuHGs0DwXYZNExY; __csrf=58a51e22ae59d859c16727cc2ac0feb9; MUSIC_U=00C81E9D33A6540B1E534BD0685ECB56A66AD5C8FB3C56421620A36C35896791D5D411693EC731D2791C68F97C67223A18058157EDA9A5674235443669115409ED466555A8A92749C0CAD9AE621FDCC89AE1AC85B8220586837DA158655C8F2A61488A9E4E9B2613A71E7A46AE7A86F5190F4E3B4E0ED70A2AA0ED51F911BA9A5398CA226EBC1DAF7603D435FD8D6883BCAA96B1F69F0BA5B72065C045F2D658D812CBC25AB44EF96C6B53CFF080BA5C9C784E89787FB64A61AA4F775B474EAA80B3CB2AA4F4C592104DD5C3A76CE3098E498A43A0BFE289BF3BA58DF66884100E4DE8F09EFB5FD6CEE8CBE35FBD3DD21A64416BBBBF9DCAA1A47285B82B7D45D6E01FC2C958AB81254408BD44FEA10C527B4F91FDA1AE310F66B3917DE4FAB7B0D3192FCD55BE291B816911BB35FA4E1E66F26CE33EBF27421F6F18AFB4C841DECD5B490FC6F88EA522819C832ABFAAD2EDAE4BFD0CCF50C79017923226CE5303; ntes_kaola_ad=1; gdxidpyhxdE=kiwV^%^2FpjaWN1XccUQvPSbTOA0p9eYHk^%^2Fud^%^2FAr8DwiQ3NLDNyhgzXozB^%^2BkOpnNsQXN2haAVp6oW2952^%^2B6JMBis8qEgYw8cUyjw^%^2BgopBqn7QYdMXpr5gg5hlBwKwYCk0QoPDSoEvTxMMxNaUk3SSVOWQZH6EUWX2dS9b7Q34efnei68cH1u^%^3A1732854332169; JSESSIONID-WYYY=gewVu7DokM2KyBU^%^2Ba5uEaH6ZWAtZu1Grc^%^2FVFlFP2Kn4P^%^2FEraFnzyqz^%^2BUCjlVAKE^%^5CbsUZ5DBoqdeDeTftrhPBHe9YNM0reygot0^%^2FAb3GfSuZmHPKvgVIerKKIZkPPuh1Wibu2DVySeNm2m893QlfjakfsyoY9VNjmJZt8Ps3fMfcf4Y2K^%^3A1732855290724; playerid=80008827^",
    "^nm-gcore-status": "1^",
    "^origin": "https://music.163.com^",
    "^priority": "u=1, i^",
    "^referer": "https://music.163.com/^",
    "^sec-ch-ua": "^\\^Chromium^^;v=^\\^130^^, ^\\^Microsoft",
    "^sec-ch-ua-mobile": "?0^",
    "^sec-ch-ua-platform": "^\\^Windows^^^",
    "^sec-fetch-dest": "empty^",
    "^sec-fetch-mode": "cors^",
    "^sec-fetch-site": "same-origin^",
    "^user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0^"
}
url = "https://music.163.com/weapi/cloudsearch/get/web?csrf_token={}".format(cookies['__csrf'])
# params = {
#     "csrf_token": "58a51e22ae59d859c16727cc2ac0feb9"
# }
js_file = open('module.js',encoding='utf-8').read()
js_code = execjs.compile(js_file)


i1x = {
    "hlpretag": "<span class=\"s-fc7\">",
    "hlposttag": "</span>",
    "s": search,
    "type": "1",
    "offset": "0",
    "total": "true",
    "limit": "30",
    "csrf_token": cookies['__csrf']
}
getany = js_code.call('get_data', i1x)
# print(getany)

data = {
    'params': getany['encText'],
    'encSecKey': getany['encSecKey'],
}

response = requests.post(url, headers=headers, data=data, cookies=cookies)
list = response.json()
item = list['result']['songs']
for s, li in enumerate(item):
    ids = li['id']
    SongName = li['name']
    singername = li['ar'][0]["name"]
    print(s + 1, SongName, singername)

songnum = input("下载哪一首：")
ID = list['result']['songs'][int(songnum) - 1]['id']
name = list['result']['songs'][int(songnum) - 1]['name']
print(ID)

a = {
    "ids": f"[{ID}]",
    "level": "standard",
    "encodeType": "aac",
    "csrf_token": cookies['__csrf']
}

getany1 = js_code.call('get_data', a)

data1 = {
    'params': getany1['encText'],
    'encSecKey': getany1['encSecKey'],
}
urls = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token={}".format(cookies['__csrf'])

response = requests.post(url=urls, headers=headers, data=data1, cookies=cookies)
data = response.json()
print(data['data'][0]['url'])

songurl = data['data'][0]['url']
download = requests.get(url = songurl, headers=headers, cookies=cookies)
with open('./音乐文件/' + f'{name}.mp3', 'wb') as f:
    f.write(download.content)
    print(f'{name}下载完成')
