import requests
import json
import base64
import re
import time
import sys
import os

# 保存所有会话的文件
SESSIONS_FILE = "spark/spark_sessions.json"

# 尝试从文件中加载所有会话
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sessions', [])
        except Exception as e:
            print(f"加载会话文件失败: {e}")
    return []

# 保存所有会话到文件
def save_sessions(sessions):
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'sessions': sessions}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存会话文件失败: {e}")

# 创建新的聊天会话
def create_new_chat(name="未命名会话"):
    headers = {
        'Content-Type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'Cookie': '[填入你的cookie]'
    }

    url = "https://xinghuo.xfyun.cn/iflygpt/u/chat-list/v1/create-chat-list"
    payload = json.dumps({})

    try:
        print("创建新会话中...")
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            chatid = response.json()['data']['id']
            print(f"会话创建成功，ID: {chatid}")
            return {
                "id": chatid,
                "name": name,
                "history": [],
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"创建会话失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"创建会话时发生错误: {e}")
        return None

# 发送消息并获取回复
def send_message(chatid, content):
    headers = {
        'Content-Type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'Cookie': 'JSESSIONID=8B010D2A5AF86E5445971B45A9469A93; account_id=20187395302; ssoSessionId=de260391-dbae-444b-a75a-55a18bfab50e'
    }

    headers1 = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'cookie': 'JSESSIONID=A7088BA4B486B3C5C87A0F18870BA89B; di_c_mti=5d6f8551-e314-61d2-8896-dc68e839be6d; d_d_app_ver=1.4.0; daas_st={%22sdk_ver%22:%221.3.9%22%2C%22status%22:%220%22}; d_d_ci=f8c73bbe-d820-6293-bdc0-1bcd96533e95; ssoSessionId=de260391-dbae-444b-a75a-55a18bfab50e; account_id=20187395302; ui=20187395302; _uetsid=438f7b2007ba11f095952ff412f839c5; _uetvid=438fd44007ba11f086535bdba1bcc1a7; _uetmsclkid=_uetb4458f42c1b214060f81e89d7a9da3bb; clientType=2; appid=fc6576da65; gt_local_id=VSv9GRfFYMGx20cA3tZ/YbCgUfaXkZ+cIpraeRggwkfd2a1UuNMIwA==; JSESSIONID=B145E29765989BB9604A58A9D5A4B4F0; account_id=20187395302; ssoSessionId=de260391-dbae-444b-a75a-55a18bfab50e'
    }

    url1 = "https://xinghuo.xfyun.cn/iflygpt-chat/u/chat_message/chat"
    params = {
        "fd": "302601",
        "isBot": "0",
        "clientType": "2",
        "chatId": f"{chatid}",
        "GtToken": "RzAwAGNroEpLh8mmBpEmCwbHf3TOws0FD4LiqT7ztKQAcdJ+P/+rSt9gAc34ufNCGyaNbATSlNUnpXgvpQDKaDF7EBMc4HuNQ6hQ4gm2DgyDcOa3QN+vxo2i9f1+77KcG64MtH3knxOvhqS7HvVQq864hpVQWtfiFrCbnVuZPlyza3Q+BbskL3bVDp7otE3BiP9gsz1lXtj8y8rkYt/sl2GfDzFx16zpKOfPur4K/02F6ty+gMD5cHrMYrHfnrMzQO3HHW9M6NaIvQfKOxais9tJyYj1FFmNO7ElyFR2w02aCsWhShzPPy22EZdafcVSdbMhL3lR2ZuXveArVPushe/zjNTsLZInWg7/3eP30ZDZ9513GSmyqxrR0TG/8CGmAtH3NcDxUNdmYI86cbkf0JWRdBFK5wU9/QSGllaZZFkcUAMmCyZIy1uhAU2Alxqkinb2ubjwq1UdWhQ0xEH9o5wtwndupkrNu7gRH/izgKjmRqbaJfgFit95It/hF121wHhR1muU+I5wJSz6554iyg0Jo2KXF9CdOoS8uMGdUMG5XwW5xxuAdFh4lWPyzos9w6IlRXmHS0junCOh9cgiegddBFql55KcdVmdyoFGSxaT3da9GJZU9nGZfYMTDQzv9CM4qrHERN3PPhXaO3F2R0TnquKjm70aRqSfnk208lx6ra65krOPOZeRLk6q3O4o2whAwyLu6gRYPt0+hAUExyp/qX9/hlob62yfzOXDAZpeOfkuqHvEw1gSrXZhU6ziWKXb5ObQ7L9ftMn8IJcVV2z5UILycNWlNxxK/UAc0ljheIzB95nJZir6lgvg2zl0LdjFxtFjjaQsae5IvsPG23TYFWC0xDHOD2B1TJKq1vJm/8QGz4APo7Hg2qeJjRW2sPJ31raXFrP/DewGzaRjdvqSXE32Pku4+3g+BCuvnCYjXZPlbvza0cBhdriCg/3d2xf4Yolpa+6w0aHQu+CblL/AgGK3AM5MdETDw50DM7hkyEImSw==",
        "text": content
    }

    try:
        print("发送消息中...")
        response = requests.request("POST", url1, headers=headers1, data=params)
        
        if response.status_code == 200:
            # 保存原始响应
            raw_response = response.text

            # 解析并解码 base64 内容
            print("\n星火AI的回答:")
            print("-" * 50)
            decoded_text = ""

            # 使用正则表达式查找所有 data:XXX 格式的内容
            data_matches = re.findall(r'data:([^<\n]+)', raw_response)

            for encoded_data in data_matches:
                if encoded_data == "<end>":
                    break
                try:
                    # 解码 base64 内容并直接输出
                    decoded_chunk = base64.b64decode(encoded_data).decode('utf-8')
                    decoded_text += decoded_chunk
                    
                    # 直接输出解码后的文本块，实现边解码边输出
                    sys.stdout.write(decoded_chunk)
                    sys.stdout.flush()
                    time.sleep(0.05)  # 适当延迟，使输出看起来更自然
                except:
                    # 忽略解码错误，不输出错误信息
                    pass

            print("\n" + "-" * 50)
            return decoded_text
        else:
            print(f"发送消息失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"发送消息时发生错误: {e}")
        return None

# 显示菜单
def show_menu():
    print("\n" + "="*50)
    print("星火AI聊天机器人")
    print("="*50)
    print("1. 新建会话")
    print("2. 继续已有会话")
    print("3. 删除会话")
    print("4. 查看会话列表")
    print("0. 退出程序")
    print("="*50)
    choice = input("请选择操作[0-4]: ")
    return choice

# 显示会话列表
def show_sessions(sessions):
    if not sessions:
        print("\n暂无会话，请创建一个新会话。")
        return None
    
    print("\n" + "="*50)
    print("会话列表:")
    print("="*50)
    for i, session in enumerate(sessions, 1):
        history_count = len(session.get('history', []))
        create_time = session.get('create_time', '未知时间')
        
        print(f"{i}. {session.get('name', '未命名')} (ID: {session.get('id', '未知')})")
        print(f"   创建时间: {create_time}, 对话数量: {history_count}")
    
    print("="*50)
    return True

# 选择会话
def select_session(sessions):
    if not show_sessions(sessions):
        return None
    
    while True:
        try:
            choice = input("请选择会话编号[1-{}] (输入'q'返回主菜单): ".format(len(sessions)))
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                return idx
            else:
                print("无效的选择，请重新输入。")
        except ValueError:
            print("请输入有效的数字。")

# 删除会话
def delete_session(sessions):
    idx = select_session(sessions)
    if idx is None:
        return False
    
    session = sessions[idx]
    confirm = input(f"确定要删除会话 '{session.get('name', '未命名')}' 吗？(y/n): ")
    if confirm.lower() == 'y':
        del sessions[idx]
        print("会话已删除。")
        return True
    
    print("已取消删除操作。")
    return False

# 创建新会话的菜单
def create_session_menu():
    name = input("请输入会话名称 (直接回车使用默认名称): ")
    if not name.strip():
        name = "未命名会话_" + time.strftime("%m%d%H%M%S")
    
    # 创建新会话
    session = create_new_chat(name)
    if session:
        print(f"已创建新会话: {name}")
        return session
    else:
        print("创建会话失败")
        return None

# 进入聊天模式
def chat_mode(session):
    print("\n" + "="*50)
    print(f"当前会话: {session.get('name', '未命名')}")
    print("="*50)
    print("输入 'q' 退出会话，输入 'menu' 显示会话内菜单")
    
    history = session.get('history', [])
    
    try:
        while True:
            content = input("\n请输入你想问的问题并回车发送（q退出）: ")
            
            if content.lower() == 'q':
                print("退出会话")
                break
            
            if content.lower() == 'menu':
                show_chat_menu(session)
                continue
            
            if not content.strip():
                print("输入不能为空，请重新输入")
                continue
            
            # 发送消息并获取回复
            assistant_response = send_message(session['id'], content)
            
            # 如果发送失败(返回None)，可能是会话过期，尝试创建新会话
            if assistant_response is None:
                print("原会话可能已过期，尝试创建新会话...")
                new_session = create_new_chat(session.get('name', '未命名'))
                if not new_session:
                    print("无法创建新会话，返回主菜单")
                    break
                
                # 更新会话ID
                session['id'] = new_session['id']
                
                # 重试发送消息
                assistant_response = send_message(session['id'], content)
                
                if assistant_response is None:
                    print("发送消息失败，请稍后再试")
                    continue
            
            # 更新对话历史
            history.append({"user": content, "assistant": assistant_response})
            session['history'] = history
            
    except KeyboardInterrupt:
        print("\n对话被中断，返回主菜单...")
    except Exception as e:
        print(f"对话过程中发生错误: {e}")
    
    return session

# 显示聊天内菜单
def show_chat_menu(session):
    print("\n" + "="*30)
    print("会话内菜单")
    print("="*30)
    print("1. 清空当前会话历史")
    print("2. 重命名会话")
    print("0. 返回对话")
    print("="*30)
    
    choice = input("请选择操作[0-2]: ")
    
    if choice == '1':
        # 清空历史
        confirm = input("确定要清空当前会话的所有历史记录吗？(y/n): ")
        if confirm.lower() == 'y':
            session['history'] = []
            print("会话历史已清空")
            
    elif choice == '2':
        # 重命名会话
        new_name = input("请输入新的会话名称: ")
        if new_name.strip():
            session['name'] = new_name
            print(f"会话已重命名为: {new_name}")
    
    print("\n返回对话...")
    return session

# 主函数
def main():
    # 加载所有会话
    sessions = load_sessions()
    
    # 主菜单循环
    try:
        while True:
            choice = show_menu()
            
            if choice == '0':
                print("\n感谢使用星火AI聊天机器人，再见！")
                break
                
            elif choice == '1':
                # 新建会话
                new_session = create_session_menu()
                if new_session:
                    sessions.append(new_session)
                    # 直接进入新会话的聊天模式
                    new_session = chat_mode(new_session)
                    # 保存所有会话
                    save_sessions(sessions)
                
            elif choice == '2':
                # 继续已有会话
                idx = select_session(sessions)
                if idx is not None:
                    session = sessions[idx]
                    # 进入聊天模式
                    session = chat_mode(session)
                    # 更新会话并保存
                    sessions[idx] = session
                    save_sessions(sessions)
                
            elif choice == '3':
                # 删除会话
                if delete_session(sessions):
                    save_sessions(sessions)
                
            elif choice == '4':
                # 查看会话列表
                show_sessions(sessions)
                input("按Enter键继续...")
                
            else:
                print("无效的选择，请重新输入。")
                
    except KeyboardInterrupt:
        print("\n程序被中断，正在保存会话状态...")
        save_sessions(sessions)
        print("会话已保存，再见！")
    except Exception as e:
        print(f"程序发生错误: {e}")
        print("正在保存会话状态...")
        save_sessions(sessions)

if __name__ == "__main__":
    main()
