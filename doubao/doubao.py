import requests
import json
import uuid
import time
import copy
import os

def generate_message_id():
    # 生成一个 UUID4 (随机 UUID)
    return f"{uuid.uuid4()}"

def extract_message_content_stream(response):
    """流式解析并输出消息内容"""
    message_content = ""
    conversation_id = None
    section_id = None
    
    print("豆包回复:")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    event_data = json.loads(data['event_data'])
                    
                    # 同时提取会话ID和分段ID
                    if 'conversation_id' in event_data and not conversation_id:
                        conversation_id = event_data['conversation_id']
                    if 'section_id' in event_data and not section_id:
                        section_id = event_data['section_id']
                    
                    # 检查是否包含消息内容
                    if 'message' in event_data and 'content' in event_data['message']:
                        content_json = json.loads(event_data['message']['content'])
                         # 提取深度思考内容
                        if 'think' in content_json:
                            think_text = content_json.get('think', '')
                            message_content += think_text
                            print(think_text, end="", flush=True)
                            time.sleep(0.01)

                        if 'text' in content_json:
                            # 直接显示消息文本
                            text_chunk = content_json['text']
                            message_content += text_chunk
                            print(text_chunk, end="", flush=True)
                            time.sleep(0.01)  # 添加小延迟使输出更自然
                except:
                    continue
    print("\n")  # 输出完成后换行
    
    # 返回消息内容和会话信息
    return {
        'message_content': message_content,
        'conversation_id': conversation_id,
        'section_id': section_id
    }

# 保存所有会话的文件
SESSIONS_FILE = "doubao_sessions.json"

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

# 创建新的会话
def create_new_session(name="未命名会话", use_deep_think=False):
    # 实际上只是创建一个结构，真正的会话ID会在第一次交互时获取
    return {
        "name": name,
        "conversation_id": None,
        "section_id": None,
        "history": [],
        "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "use_deep_think": use_deep_think
    }

# 发送消息
def send_message(session, content):
    url = "https://www.doubao.com/samantha/chat/completion?aid=497858&device_id=7475953414271796770&device_platform=web&language=zh&pc_version=2.11.0&pkg_type=release_version&real_aid=497858&region=CN&samantha_web=1&sys_region=CN&tea_uuid=7475953427333531175&use-olympus-account=1&version_code=20800&web_id=7475953427333531175&msToken=T0SY1X_ikWLaWU28JxFmTfRUah3hkqmvR3iKE88246HM77EHltdMTVYkwSb6tRE8GGQ3WQRIDMOtf3FZymWtWttZVY67PviM-7MBkr2IKM187vYpDUv7iQ%3D%3D&a_bogus=EjUDvchmMsm1F9YV8wkz9tajs9E0YW-HgZEN2EztitLp"

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'agw-js-conv': 'str',
        'content-type': 'application/json',
        'last-event-id': 'undefined',
        'origin': 'https://www.doubao.com',
        'priority': 'u=1, i',
        'referer': 'https://www.doubao.com/chat/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'x-flow-trace': '04-0010dc95e66f2cd00016171f172d6172-000d5d348c67cfaf-01',
        'Cookie': '[填入你的cookie]'
    }

    # 判断是新会话还是继续会话
    if session['conversation_id'] is None or session['section_id'] is None:
        # 新会话的情况
        payload = json.dumps({
            "messages": [
                {
                    "content": json.dumps({"text": content}),
                    "content_type": 2001,
                    "attachments": [],
                    "references": []
                }
            ],
            "completion_option": {
                "is_regen": False,
                "with_suggest": True,
                "need_create_conversation": True,
                "launch_stage": 1,
                "is_replace": False,
                "is_delete": False,
                "message_from": 0,
                "use_deep_think": session['use_deep_think'],
                "event_id": "0"
            },
            "conversation_id": "0",
            "local_conversation_id": "local_" + str(int(time.time() * 1000)),
            "local_message_id": generate_message_id()
        })
    else:
        # 继续会话的情况
        payload = json.dumps({
            "messages": [
                {
                    "content": json.dumps({"text": content}),
                    "content_type": 2001,
                    "attachments": [],
                    "references": []
                }
            ],
            "completion_option": {
                "is_regen": False,
                "with_suggest": True,
                "need_create_conversation": False,
                "launch_stage": 1,
                "is_replace": False,
                "is_delete": False,
                "message_from": 0,
                "use_deep_think": session['use_deep_think'],
                "event_id": "0"
            },
            "section_id": session['section_id'],
            "conversation_id": session['conversation_id'],
            "local_message_id": generate_message_id()
        })

    try:
        response = requests.request("POST", url, headers=headers, data=payload, stream=True)
        result = extract_message_content_stream(response)
        
        # 更新会话信息（如果是第一次请求）
        if session['conversation_id'] is None:
            session['conversation_id'] = result['conversation_id']
            session['section_id'] = result['section_id']
            print(f"已获取会话ID: {session['conversation_id']}")
            print(f"已获取分段ID: {session['section_id']}")
        
        # 添加对话历史
        session['history'].append({
            "user": content,
            "assistant": result['message_content']
        })
        
        return result['message_content']
    except Exception as e:
        print(f"发送消息失败: {e}")
        return None

# 显示菜单
def show_menu():
    print("\n" + "="*50)
    print("豆包聊天机器人命令行客户端")
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
        use_deep_think = "是" if session.get('use_deep_think', False) else "否"
        
        print(f"{i}. {session.get('name', '未命名')} (ID: {session.get('conversation_id', '未获取')})")
        print(f"   创建时间: {create_time}, 对话数量: {history_count}")
        print(f"   使用深度思考: {use_deep_think}")
    
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
    
    # 获取深度思考设置
    while True:
        think_choice = input("是否启用深度思考？(y/n): ")
        if think_choice.lower() in ['y', 'n']:
            use_deep_think = think_choice.lower() == 'y'
            break
        else:
            print("无效的选择，请重新输入。")
    
    # 创建新会话
    session = create_new_session(name, use_deep_think)
    print(f"已创建新会话: {name}")
    return session

# 进入聊天模式
def chat_mode(session):
    print("\n" + "="*50)
    print(f"当前会话: {session.get('name', '未命名')}")
    print(f"使用深度思考: {'是' if session.get('use_deep_think', False) else '否'}")
    print("="*50)
    print("输入 'q' 退出会话，输入 'menu' 显示会话内菜单")
    
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
            send_message(session, content)
            
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
    print("1. 开关深度思考功能")
    print("2. 清空当前会话历史")
    print("3. 重命名会话")
    print("0. 返回对话")
    print("="*30)
    
    choice = input("请选择操作[0-3]: ")
    
    if choice == '1':
        # 开关深度思考功能
        current = session.get('use_deep_think', False)
        session['use_deep_think'] = not current
        status = "开启" if session['use_deep_think'] else "关闭"
        print(f"深度思考功能已{status}")
        
    elif choice == '2':
        # 清空历史
        confirm = input("确定要清空当前会话的所有历史记录吗？(y/n): ")
        if confirm.lower() == 'y':
            session['history'] = []
            print("会话历史已清空")
            
    elif choice == '3':
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
                print("\n感谢使用豆包聊天机器人，再见！")
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

