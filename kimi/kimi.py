import requests
import brotli
import json
import os
import argparse
import sys
import time

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'authorization': '[填入你的token]',
    'content-type': 'application/json',
    'referer': 'https://kimi.moonshot.cn/chat/empty',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'connection': 'keep-alive'
}

# 调试模式
DEBUG = False  # 设置为True开启调试输出

# 请求超时设置(秒)
REQUEST_TIMEOUT = 30

# 保存所有会话的文件
SESSIONS_FILE = "kimi_sessions.json"

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

# 创建新会话
def create_new_session(name="未命名会话"):
    url = 'https://kimi.moonshot.cn/api/chat'
    data = {
        "name": name,
        "born_from": "chat",
        "kimiplus_id": "kimi",
        "is_example": False,
        "source": "web",
        "tags": []
    }
    
    try:
        print("创建新会话中...")
        response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            if 'content-encoding' in response.headers and response.headers['content-encoding'] == 'br':
                decompressed_data = brotli.decompress(response.content)
                response_data = json.loads(decompressed_data)
            else:
                response_data = response.json()
            
            session_id = response_data['id']
            print(f"会话创建成功，ID: {session_id}")
            return {
                "id": session_id,
                "name": name,
                "history": [],
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": "k1",
                "use_search": True
            }
            
        else:
            print(f"创建会话失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("创建会话请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("创建会话连接错误，请检查网络")
        return None
    except Exception as e:
        print(f"创建会话时发生错误: {e}")
        return None

# 发送消息并处理回复
def send_message(session_id, content, history, model, use_search):
    url = f'https://kimi.moonshot.cn/api/chat/{session_id}/completion/stream'
    
    # 构建消息历史
    messages = []
    for item in history:
        messages.append({"role": "user", "content": item["user"]})
        if item.get("assistant"):
            messages.append({"role": "assistant", "content": item["assistant"]})
    
    # 添加当前消息
    messages.append({"role": "user", "content": content})
    
    data = {
        "kimiplus_id": "kimi",
        "extend": {
            "sidebar": True
        },
        "model": model,
        "use_research": False,
        "use_search": use_search,  
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "refs": [],
        "history": [], 
        "scene_labels": []
    }
    
    try:
        print("发送消息中...")
        start_time = time.time()
        with requests.post(url, headers=headers, json=data, stream=True, timeout=REQUEST_TIMEOUT) as response:
            elapsed_time = time.time() - start_time
            print(f"响应状态码: {response.status_code}, 请求耗时: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                print("\nKimi回复：")
                full_answer = ""
                k1_answer = ""  # k1事件的回复
                cmpl_answer = ""  # cmpl事件的回复
                has_cmpl = False  # 是否有cmpl事件
                has_done = False  # 是否收到done事件
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        
                        if DEBUG:
                            print(f"\n原始行: {line}")
                        
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                event_type = data.get('event', '')
                                
                                # 调试信息
                                if DEBUG:
                                    print(f"事件类型: {event_type}, 数据: {data}")
                                
                                # 处理k1类型的文本事件
                                if event_type == 'k1' and data.get('type') == 'text':
                                    text = data.get('text', '')
                                    k1_answer += text
                                    print(text, end="", flush=True)
                                
                                # 处理cmpl类型的文本事件
                                elif event_type == 'cmpl':
                                    has_cmpl = True
                                    if 'text' in data and not data.get('loading', False):
                                        text = data.get('text', '')
                                        if text: # 只有当text不为空时才添加
                                            cmpl_answer += text
                                            print(text, end="", flush=True)
                                
                                # 处理done事件
                                elif event_type == 'done':
                                    has_done = True
                                    if DEBUG:
                                        print("\n[回复第一阶段完成]")
                                
                                # 处理all_done事件
                                elif event_type == 'all_done':
                                    if DEBUG:
                                        print("\n[全部回复完成]")
                                
                                # 处理summary事件
                                elif event_type == 'k1' and 'summary' in data:
                                    summary = data.get('summary', '')
                                    if DEBUG:
                                        print(f"\n[摘要: {summary}]")
                                
                            except json.JSONDecodeError as e:
                                if DEBUG:
                                    print(f"JSON解析错误: {e}, 原始行: {line}")
                                continue
                
                # 组装完整回答
                # 某些情况下，cmpl事件返回的可能是完整的新回复，而不是对k1的补充
                if has_cmpl and cmpl_answer and not (has_done and cmpl_answer in k1_answer):
                    full_answer = cmpl_answer
                else:
                    full_answer = k1_answer
                
                if DEBUG:
                    print("\n\nK1回复: " + k1_answer)
                    print("\nCMPL回复: " + cmpl_answer)
                    print("\n完整回复: " + full_answer)
                
                return full_answer
            else:
                print(f"发送消息失败，状态码: {response.status_code}")
                if response.status_code == 404:
                    print("会话可能已过期，尝试创建新会话...")
                    return None
                print(f"响应内容: {response.text}")
                return None
    
    except requests.exceptions.Timeout:
        print("请求超时，请检查网络连接或服务器状态")
        return None        
    except requests.exceptions.ConnectionError:
        print("连接错误，请检查网络")
        return None
    except Exception as e:
        print(f"发送消息时发生错误: {e}")
        return None

# 显示菜单
def show_menu():
    print("\n" + "="*50)
    print("Kimi 聊天机器人命令行客户端")
    print("="*50)
    print("1. 新建会话")
    print("2. 继续已有会话")
    print("3. 删除会话")
    print("4. 查看会话列表")
    print("5. 设置默认模型和搜索选项")
    print("0. 退出程序")
    print("="*50)
    choice = input("请选择操作[0-5]: ")
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
        model = session.get('model', 'k1')
        use_search = "是" if session.get('use_search', True) else "否"
        
        print(f"{i}. {session.get('name', '未命名')} (ID: {session.get('id', '未知')})")
        print(f"   创建时间: {create_time}, 对话数量: {history_count}")
        print(f"   模型: {model}, 使用搜索: {use_search}")
    
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

# 设置默认的模型和搜索选项
def set_defaults():
    print("\n" + "="*50)
    print("设置默认选项")
    print("="*50)
    
    # 显示可用的模型选项
    print("可用模型:")
    print("1. k1 (Kimi 1.5)")
    print("2. kimi (原老模型)")
    
    while True:
        model_choice = input("请选择默认模型 [1-2]: ")
        if model_choice == '1':
            model = 'k1'
            break
        elif model_choice == '2':
            model = 'kimi'
            break
        else:
            print("无效的选择，请重新输入。")
    
    while True:
        search_choice = input("是否默认启用搜索功能？(y/n): ")
        if search_choice.lower() in ['y', 'n']:
            use_search = search_choice.lower() == 'y'
            break
        else:
            print("无效的选择，请重新输入。")
    
    return {
        "model": model,
        "use_search": use_search
    }

# 创建新会话的菜单
def create_session_menu():
    name = input("请输入会话名称 (直接回车使用默认名称): ")
    if not name.strip():
        name = "未命名会话_" + time.strftime("%m%d%H%M%S")
    
    # 获取默认设置
    defaults = set_defaults()
    
    # 创建新会话
    session = create_new_session(name)
    if session:
        # 添加默认设置
        session['model'] = defaults['model']
        session['use_search'] = defaults['use_search']
        print(f"已创建新会话: {name}")
        return session
    else:
        print("创建会话失败")
        return None

# 进入聊天模式
def chat_mode(session):
    print("\n" + "="*50)
    print(f"当前会话: {session.get('name', '未命名')}")
    print(f"模型: {session.get('model', 'k1')}, 使用搜索: {'是' if session.get('use_search', True) else '否'}")
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
            assistant_response = send_message(
                session['id'], 
                content, 
                history, 
                session.get('model', 'k1'), 
                session.get('use_search', True)
            )
            
            # 如果发送失败(返回None)，可能是会话过期，尝试创建新会话
            if assistant_response is None:
                print("原会话可能已过期，尝试创建新会话...")
                new_session = create_new_session(session.get('name', '未命名'))
                if not new_session:
                    print("无法创建新会话，返回主菜单")
                    break
                
                # 更新会话ID和设置
                session['id'] = new_session['id']
                
                # 重试发送消息
                assistant_response = send_message(
                    session['id'], 
                    content, 
                    history, 
                    session.get('model', 'k1'), 
                    session.get('use_search', True)
                )
                
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
    print("1. 更改模型")
    print("2. 开关搜索功能")
    print("3. 清空当前会话历史")
    print("4. 重命名会话")
    print("0. 返回对话")
    print("="*30)
    
    choice = input("请选择操作[0-4]: ")
    
    if choice == '1':
        # 更改模型
        print("可用模型:")
        print("1. k1 (Kimi 1.5)")
        print("2. kimi (新版本)")
        
        model_choice = input("请选择模型 [1-2]: ")
        if model_choice == '1':
            session['model'] = 'k1'
        elif model_choice == '2':
            session['model'] = 'kimi'
        print(f"模型已更改为: {session['model']}")
        
    elif choice == '2':
        # 开关搜索功能
        current = session.get('use_search', True)
        session['use_search'] = not current
        status = "开启" if session['use_search'] else "关闭"
        print(f"搜索功能已{status}")
        
    elif choice == '3':
        # 清空历史
        confirm = input("确定要清空当前会话的所有历史记录吗？(y/n): ")
        if confirm.lower() == 'y':
            session['history'] = []
            print("会话历史已清空")
            
    elif choice == '4':
        # 重命名会话
        new_name = input("请输入新的会话名称: ")
        if new_name.strip():
            session['name'] = new_name
            print(f"会话已重命名为: {new_name}")
    
    print("\n返回对话...")
    return session

# 主函数
def main():
    global DEBUG
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Kimi聊天机器人命令行客户端')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间(秒)')
    args = parser.parse_args()
    
    # 设置调试模式
    DEBUG = args.debug
    if DEBUG:
        print("调试模式已启用")
    
    # 设置超时
    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = args.timeout
    
    # 加载所有会话
    sessions = load_sessions()
    
    # 主菜单循环
    try:
        while True:
            choice = show_menu()
            
            if choice == '0':
                print("\n感谢使用Kimi聊天机器人，再见！")
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
                
            elif choice == '5':
                # 设置默认选项
                defaults = set_defaults()
                print(f"默认选项已设置：模型={defaults['model']}, 使用搜索={'是' if defaults['use_search'] else '否'}")
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