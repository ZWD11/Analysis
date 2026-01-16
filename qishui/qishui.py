import json
import re
import os
import requests
from urllib.parse import urlencode

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def curl(url, timeout=10):
    """发送HTTP请求"""
    headers = {
      'Host': 'api.qishui.com',
      'Connection':'keep-alive',
      'X-Helios': 'ZH4AADUIdsFOZKI+I/R9GFEfafOXE16cupq5lr2RdaL/+Ozc',
      'X-Medusa': 'lThnaWHQOJNB77tSQBKvGcH3BnEaPgMB/rdRF2BAASQzmXknPjtHC6qU31dVz6//UYTj6HthKEE8kz89+eKtBL0eYfyk2aNNseLQp+GPKWv75libC4u/pwbJlX1iy+iCM/7+cwUuyzmAiOVotYq2bu1ynlUachONh848M3BcYSA6RFiNLGTRyypqDXojtsw/Vk0O95NHyRF6/RXP6era0ChXVh6KZKh41HJfsqz721CuoXatRf818erCcV4+OJAxlDNiNQ5W28gRwWLcziR7Z/IJRN+pfg5SJU9bUcmSZSAvlms4ciyV6WjHxZrHo0Jy/CeEmvvMv6lnfm5pdZYU6rmYLt9N6jfnEjqNDBgbS+g3y1kslRofNmjRrs+I3g6H9a2v8my9XnzSjoSAcSaJ0Uen0fuGPRxg/zWgmIOmDyEYNYkGF8CyjoVYzKQHxxVQ0Z+V3ueasYwYxioCfbeR37VtgFHN9dI2sXJFwVrgYEv8GvCAH53fzwH/Zs4LECgyYNUkiyfvXNrPQ2Exc6i4tla6uL2Xui2C4GKgGZkOVUCQFzoI91kZUaFc5IOGkwDyU51YMz306tdtkGHO2t4EUWl9dbmgtyHTzZeJbAJUGTJwaBvYMALnUU+1PHuAEBPhP3XwzOdb5vEOD5GWrIXLYALowVjG+yf5mkN1vi0JoUe9959YV/MJ2rSCiGxA0/FmbNom++4yAJ/rbfhv8PU8JaYiZMToypUhLZS/C9kXnDCwqxF0qCJjYhPu69MJ74GLL2lPrT/r11OvLW/Nv83lZQl/yB4+7q+eP52Y1renj64eZSfXH4kXFLmdjd5x59kP517Qum9nZQnkI5xoldAHKB5l+////+///v8AAA==',
      'user-agent': 'LunaPC/3.0.0(290101097)',
      'x-luna-background-type': 'foreground',
      'x-luna-is-background-req': '0',
      'x-luna-is-local-user': '1',
      'x-tt-trace-id': '00-bb350c9d010e8734f2bc579a2fd00000-bb350c9d010e8734-01',
      'Accept-Encoding': 'gzip, deflate'
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        return response.text
    except Exception as e:
        print(f"请求错误: {e}")
        return None


def download_file(url, filename):
    """下载文件"""
    try:
        print(f"正在下载: {filename}")
        response = requests.get(url, timeout=30, verify=False)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"下载完成: {filename}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False


def convert_krc_to_lrc(krc_content):
    """将KRC歌词转换为LRC格式"""
    cleaned_content = re.sub(r'<\d+,\d+,\d+>', '', krc_content)
    
    match = re.match(r'\[(\d+),(\d+)\](.*)', cleaned_content)
    if not match:
        return ""
    
    start_time = int(match.group(1))
    lyrics = match.group(3)
    
    minutes = start_time // 60000
    seconds = (start_time // 1000) % 60
    centiseconds = (start_time % 1000) // 10
    
    lrc_content = f"[{minutes:02d}:{seconds:02d}.{centiseconds:02d}]{lyrics}\n"
    return lrc_content


def krc_to_lrc(content):
    """歌词krc转lrc"""
    if not content:
        return ""
    content = content.rstrip('\n')
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        converted = convert_krc_to_lrc(line)
        if converted:
            new_lines.append(converted)
    
    new_text = ''.join(new_lines)
    return new_text


def search_music(keyword):
    """搜索音乐"""
    params = {
        "aid": "386088",
        "app_name": "luna_pc",
        "region": "cn",
        "geo_region": "cn",
        "os_region": "cn",
        "sim_region": "",
        "device_id": "1088932190113307",
        "cdid": "",
        "iid": "2332504177791808",
        "version_name": "3.0.0",
        "version_code": "30000000",
        "channel": "official",
        "build_mode": "master",
        "network_carrier": "",
        "ac": "wifi",
        "tz_name": "Asia/Shanghai",
        "resolution": "",
        "device_platform": "windows",
        "device_type": "Windows",
        "os_version": "Windows 11 Home China",
        "fp": "1088932190113307",
        "q": keyword,
        "cursor": "0", # 值为0、20、40...相当于翻页，20一页,0就默认前20首
        "search_id": "4ee2bc52-db9b-42c3-85cf-cdac2fe02efe",
        "search_method": "input",
        "debug_params": "",
        "from_search_id": "1aa21093-d49e-4d29-b6c7-548b170d12a0",
        "search_scene": ""
    }
        
    url = 'https://api.qishui.com/luna/pc/search/track?' + urlencode(params)
    response_text = curl(url)
    
    if not response_text:
        print("搜索失败")
        return None
    
    try:
        json_data = json.loads(response_text)
        data = json_data.get('result_groups', [{}])[0].get('data', [])
        return data
    except Exception as e:
        print(f"解析搜索结果失败: {e}")
        return None


def get_music_info(track_id):
    """获取音乐详细信息"""
    url = f'https://api.qishui.com/luna/h5/track?track_id={track_id}'
    response = curl(url)
    
    if not response:
        print("获取音乐信息失败")
        return None
    
    try:
        data = json.loads(response)
    except:
        print("解析数据失败")
        return None

    lyrics = data.get('lyric', {}).get('content', '')
    
    # 获取音乐URL
    url_player_info = data.get('track_player', {}).get('url_player_info')
    video_model = data.get('track_player', {}).get('video_model')
    
    music = None
    if url_player_info:
        try:
            player_data = json.loads(url_player_info)
            music = player_data.get('video_list', [{}])[0].get('main_url')
        except:
            pass
    
    if not music and video_model:
        try:
            video_data = json.loads(video_model)
            music = video_data.get('video_list', [{}])[0].get('backup_url')
        except:
            pass
    
    title = data.get('track', {}).get('name', '')
    
    # 获取歌手信息
    artists = data.get('track', {}).get('artists', [])
    singers = []
    for singer in artists:
        singers.append(singer.get('name', ''))
    singer = '&'.join(singers) if singers else '未知歌手'
    
    # 获取封面
    album = data.get('track', {}).get('album', {})
    url_cover = album.get('url_cover', {})
    cover_urls = url_cover.get('urls', [''])
    cover_uri = url_cover.get('uri', '')
    cover = cover_urls[0] + cover_uri + '~c5_375x375.jpg' if cover_urls else ''
    
    lrc = krc_to_lrc(lyrics).replace('\n\n', '\n')
    
    return {
        'title': title,
        'singer': singer,
        'music': music,
        'cover': cover,
        'lrc': lrc
    }


def sanitize_filename(filename):
    """清理文件名，移除不合法字符"""
    # 移除或替换不合法字符
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    return filename


def main():
    print("=" * 50)
    print("汽水音乐搜索与下载工具")
    print("=" * 50)
    
    while True:
        # 输入搜索关键词
        keyword = input("\n请输入要搜索的歌曲名称 (输入q退出): ").strip()
        
        if keyword.lower() == 'q':
            print("再见!")
            break
        
        if not keyword:
            print("请输入有效的关键词")
            continue
        
        # 搜索歌曲
        print(f"\n正在搜索: {keyword}...")
        results = search_music(keyword)
        
        if not results:
            print("未找到相关歌曲")
            continue
        
        # 显示搜索结果
        print(f"\n找到 {len(results)} 首歌曲:\n")
        print(f"{'序号':<6}{'歌名':<30}{'歌手':<20}")
        print("-" * 60)
        
        song_list = []
        for i, item in enumerate(results):
            track = item.get('entity', {}).get('track', {})
            artists = track.get('artists', [])
            
            singers = []
            for singer in artists:
                singers.append(singer.get('name', ''))
            singer_str = '&'.join(singers) if singers else '未知歌手'
            
            title = track.get('name', '未知')
            track_id = track.get('id', '')
            
            song_list.append({
                'title': title,
                'singer': singer_str,
                'track_id': track_id
            })
            
            print(f"{i+1:<6}{title[:28]:<30}{singer_str[:18]:<20}")
        
        # 选择歌曲
        while True:
            choice = input("\n请输入要下载的歌曲序号 (输入0返回搜索): ").strip()
            
            if choice == '0':
                break
            
            try:
                num = int(choice)
                if num < 1 or num > len(song_list):
                    print(f"请输入 1-{len(song_list)} 之间的数字")
                    continue
                
                selected = song_list[num - 1]
                print(f"\n已选择: {selected['title']} - {selected['singer']}")
                
                # 获取音乐信息
                print("正在获取音乐信息...")
                info = get_music_info(selected['track_id'])
                
                if not info:
                    print("获取音乐信息失败")
                    continue
                
                print(f"歌名: {info['title']}")
                print(f"歌手: {info['singer']}")
                print(f"歌曲id: {selected['track_id']}")
                
                if not info['music']:
                    print("无法获取音乐链接")
                    continue
                
                # 创建下载目录
                download_dir = "downloaded_music"
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                
                # 清理文件名
                safe_title = sanitize_filename(info['title'])
                safe_singer = sanitize_filename(info['singer'])
                base_filename = f"{safe_title} - {safe_singer}"
                
                # 下载音乐
                music_ext = '.mp3'  # 默认扩展名
                music_filename = os.path.join(download_dir, base_filename + music_ext)
                
                if download_file(info['music'], music_filename):
                    # 保存歌词
                    if info['lrc']:
                        lrc_filename = os.path.join(download_dir, base_filename + '.txt')
                        try:
                            with open(lrc_filename, 'w', encoding='utf-8') as f:
                                f.write(info['lrc'])
                            print(f"歌词已保存: {lrc_filename}")
                        except Exception as e:
                            print(f"保存歌词失败: {e}")
                    else:
                        print("该歌曲没有歌词")
                    
                    print(f"\n下载完成! 文件保存在: {download_dir} 目录")
                
                break
                
            except ValueError:
                print("请输入有效的数字")
            except Exception as e:
                print(f"发生错误: {e}")


if __name__ == '__main__':
    main()