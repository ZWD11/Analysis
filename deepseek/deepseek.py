import base64
import ctypes
import json
import logging
import struct
import argparse
import os
import time
import sys
from wasmtime import Linker, Module, Store
from curl_cffi import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepseek_cli")

# 调试模式
DEBUG = False

# 请求超时设置(秒)
REQUEST_TIMEOUT = 30

# 保存所有会话的文件
SESSIONS_FILE = "deepseek/deepseek_sessions.json"

# DeepSeek 相关常量
DEEPSEEK_HOST = "chat.deepseek.com"
DEEPSEEK_CREATE_POW_URL = f"https://{DEEPSEEK_HOST}/api/v0/chat/create_pow_challenge"
BASE_HEADERS = {
    "Host": "chat.deepseek.com",
    "User-Agent": "DeepSeek/1.0.13 Android/35",
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "x-client-platform": "android",
    "x-client-version": "1.0.13",
    "x-client-locale": "zh_CN",
    "accept-charset": "UTF-8",
}

# WASM 文件路径
WASM_PATH = "deepseek/sha3_wasm_bg.7b9ca65ddd.wasm"

# 尝试从文件中加载所有会话
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sessions', [])
        except Exception as e:
            logger.error(f"加载会话文件失败: {e}")
    return []

# 保存所有会话到文件
def save_sessions(sessions):
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'sessions': sessions}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存会话文件失败: {e}")

def compute_pow_answer(
    algorithm: str,
    challenge_str: str, 
    salt: str,
    difficulty: int,
    expire_at: int,
    signature: str,
    target_path: str,
    wasm_path: str,
) -> int:
    """使用 WASM 模块计算 PoW 答案"""
    if algorithm != "DeepSeekHashV1":
        raise ValueError(f"不支持的算法：{algorithm}")
        
    prefix = f"{salt}_{expire_at}_"
    
    # 加载 wasm 模块
    store = Store()
    linker = Linker(store.engine)
    try:
        with open(wasm_path, "rb") as f:
            wasm_bytes = f.read()
    except Exception as e:
        raise RuntimeError(f"加载 wasm 文件失败: {wasm_path}, 错误: {e}")
        
    module = Module(store.engine, wasm_bytes)
    instance = linker.instantiate(store, module)
    exports = instance.exports(store)
    
    try:
        memory = exports["memory"]
        add_to_stack = exports["__wbindgen_add_to_stack_pointer"]
        alloc = exports["__wbindgen_export_0"]
        wasm_solve = exports["wasm_solve"]
    except KeyError as e:
        raise RuntimeError(f"缺少 wasm 导出函数: {e}")

    def write_memory(offset: int, data: bytes):
        size = len(data)
        base_addr = ctypes.cast(memory.data_ptr(store), ctypes.c_void_p).value
        ctypes.memmove(base_addr + offset, data, size)

    def read_memory(offset: int, size: int) -> bytes:
        base_addr = ctypes.cast(memory.data_ptr(store), ctypes.c_void_p).value
        return ctypes.string_at(base_addr + offset, size)

    def encode_string(text: str):
        data = text.encode("utf-8")
        length = len(data)
        ptr_val = alloc(store, length, 1)
        ptr = int(ptr_val.value) if hasattr(ptr_val, "value") else int(ptr_val)
        write_memory(ptr, data)
        return ptr, length

    # 1. 申请栈空间
    retptr = add_to_stack(store, -16)
    
    # 2. 编码字符串到内存
    ptr_challenge, len_challenge = encode_string(challenge_str)
    ptr_prefix, len_prefix = encode_string(prefix)
    
    # 3. 调用 wasm_solve
    wasm_solve(store, retptr, ptr_challenge, len_challenge, ptr_prefix, len_prefix, float(difficulty))
    
    # 4. 读取结果
    status_bytes = read_memory(retptr, 4)
    if len(status_bytes) != 4:
        add_to_stack(store, 16)
        raise RuntimeError("读取状态字节失败")
    status = struct.unpack("<i", status_bytes)[0]
    
    value_bytes = read_memory(retptr + 8, 8)
    if len(value_bytes) != 8:
        add_to_stack(store, 16)
        raise RuntimeError("读取结果字节失败")
    value = struct.unpack("<d", value_bytes)[0]
    
    # 5. 恢复栈指针
    add_to_stack(store, 16)
    
    if status == 0:
        return None
    return int(value)

def get_pow_response(token: str, max_attempts=3):
    """获取 PoW challenge 并计算答案"""
    headers = {**BASE_HEADERS, "authorization": f"Bearer {token}"}
    
    for attempt in range(max_attempts):
        try:
            resp = requests.post(
                DEEPSEEK_CREATE_POW_URL,
                headers=headers,
                json={"target_path": "/api/v0/chat/completion"},
                timeout=30
            )
            
            data = resp.json()
            if resp.status_code == 200 and data.get("code") == 0:
                challenge = data["data"]["biz_data"]["challenge"]
                difficulty = challenge.get("difficulty", 144000)
                expire_at = challenge.get("expire_at", 1680000000)
                
                # 关闭响应连接
                resp.close()
                
                try:
                    answer = compute_pow_answer(
                        challenge["algorithm"],
                        challenge["challenge"],
                        challenge["salt"],
                        difficulty,
                        expire_at,
                        challenge["signature"],
                        challenge["target_path"],
                        WASM_PATH
                    )
                except Exception as e:
                    logger.error(f"PoW 答案计算异常: {e}")
                    continue
                    
                if answer is None:
                    logger.warning("PoW 答案计算失败，重试中...")
                    continue
                    
                pow_dict = {
                    "algorithm": challenge["algorithm"],
                    "challenge": challenge["challenge"],
                    "salt": challenge["salt"],
                    "answer": answer,
                    "signature": challenge["signature"],
                    "target_path": challenge["target_path"],
                }
                
                pow_str = json.dumps(pow_dict, separators=(",", ":"), ensure_ascii=False)
                encoded = base64.b64encode(pow_str.encode("utf-8")).decode("utf-8").rstrip()
                return encoded
                
            else:
                # 关闭响应连接
                resp.close()
                logger.warning(f"获取 PoW 失败, code={data.get('code')}, msg={data.get('msg')}")
                
        except Exception as e:
            try:
                # 尝试关闭响应连接
                if 'resp' in locals() and resp is not None:
                    resp.close()
            except:
                pass
            logger.error(f"请求异常: {e}")
            
    return None

# 创建新会话
def create_new_session(token, name="未命名会话", use_search=True, use_thinking=False):
    """创建新的DeepSeek会话"""
    # 获取POW响应
    pow_response = get_pow_response(token)
    if not pow_response:
        print("获取PoW失败，无法创建会话")
        return None
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'referer': 'https://chat.deepseek.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'connection': 'keep-alive',
        'x-ds-pow-response': pow_response
    }

    url = 'https://chat.deepseek.com/api/v0/chat_session/create'
    data = {"character_id": None}
    
    try:
        print("创建新会话中...")
        response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('code') == 0:
                session_id = response_data['data']['biz_data']['id']
                print(f"会话创建成功，ID: {session_id}")
                # 确保关闭连接
                response.close()
                return {
                    "id": session_id,
                    "name": name,
                    "history": [],
                    "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "use_search": use_search,
                    "use_thinking": use_thinking
                }
        
        print(f"创建会话失败，状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        # 确保关闭连接
        response.close()
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

# 发送消息并处理流式回复
def send_message(token, session_id, content, history, use_search=True, use_thinking=False):
    # 获取POW响应
    pow_response = get_pow_response(token)
    if not pow_response:
        print("获取PoW失败，无法发送消息")
        return None
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'referer': 'https://chat.deepseek.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
        'connection': 'keep-alive',
        'x-ds-pow-response': pow_response
    }

    # 获取父消息ID（如果有的话）
    parent_message_id = None
    if history and len(history) > 0:
        last_message = history[-1]
        if last_message.get('parent_message_id'):
            parent_message_id = last_message.get('parent_message_id')
        elif last_message.get('message_id'):
            parent_message_id = last_message.get('message_id')
    
    url = 'https://chat.deepseek.com/api/v0/chat/completion'
    data = {
        "chat_session_id": session_id,
        "parent_message_id": parent_message_id,
        "prompt": content,
        "ref_file_ids": [],
        "thinking_enabled": use_thinking,
        "search_enabled": use_search
    }
    
    try:
        print("发送消息中...")
        start_time = time.time()
        
        # 不使用with语句，改为直接调用方式
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=REQUEST_TIMEOUT)
        
        elapsed_time = time.time() - start_time
        print(f"响应状态码: {response.status_code}, 请求耗时: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            print("\nDeepSeek回复：")
            full_answer = ""
            message_id = None
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    if DEBUG:
                        print(f"\n原始行: {line}")
                    
                    if line.startswith('data: '):
                        if line == 'data: [DONE]':
                            if DEBUG:
                                print("\n[回复完成]")
                            break
                            
                        try:
                            data = json.loads(line[6:])
                            
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    text = choice['delta']['content']
                                    if text:  # 有些delta可能没有content或content为空
                                        full_answer += text
                                        print(text, end="", flush=True)
                                
                                # 记录消息ID（用于维护对话历史）
                                if message_id is None and 'message_id' in data:
                                    message_id = data['message_id']
                            
                        except json.JSONDecodeError as e:
                            if DEBUG:
                                print(f"JSON解析错误: {e}, 原始行: {line}")
                            continue
            
            # 关闭响应连接
            response.close()
            
            print("\n")
            return {
                "content": full_answer,
                "message_id": message_id,
                "parent_message_id": parent_message_id
            }
        else:
            print(f"发送消息失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            # 确保关闭连接
            response.close()
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
    print("DeepSeek 聊天机器人命令行客户端")
    print("="*50)
    print("1. 新建会话")
    print("2. 继续已有会话")
    print("3. 删除会话")
    print("4. 查看会话列表")
    print("5. 设置默认搜索和思考选项")
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
        use_search = "是" if session.get('use_search', True) else "否"
        use_thinking = "是" if session.get('use_thinking', False) else "否"
        
        print(f"{i}. {session.get('name', '未命名')} (ID: {session.get('id', '未知')})")
        print(f"   创建时间: {create_time}, 对话数量: {history_count}")
        print(f"   使用搜索: {use_search}, 使用思考: {use_thinking}")
    
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

# 设置默认的搜索和思考选项
def set_defaults():
    print("\n" + "="*50)
    print("设置默认选项")
    print("="*50)
    
    while True:
        search_choice = input("是否默认启用搜索功能？(y/n): ")
        if search_choice.lower() in ['y', 'n']:
            use_search = search_choice.lower() == 'y'
            break
        else:
            print("无效的选择，请重新输入。")
    
    while True:
        thinking_choice = input("是否默认启用思考功能(R1)？(y/n): ")
        if thinking_choice.lower() in ['y', 'n']:
            use_thinking = thinking_choice.lower() == 'y'
            break
        else:
            print("无效的选择，请重新输入。")
    
    return {
        "use_search": use_search,
        "use_thinking": use_thinking
    }

# 创建新会话的菜单
def create_session_menu(token):
    name = input("请输入会话名称 (直接回车使用默认名称): ")
    if not name.strip():
        name = "未命名会话_" + time.strftime("%m%d%H%M%S")
    
    # 获取默认设置
    defaults = set_defaults()
    
    # 创建新会话
    session = create_new_session(
        token=token, 
        name=name, 
        use_search=defaults["use_search"], 
        use_thinking=defaults["use_thinking"]
    )
    
    if session:
        print(f"已创建新会话: {name}")
        return session
    else:
        print("创建会话失败")
        return None

# 进入聊天模式
def chat_mode(token, session):
    print("\n" + "="*50)
    print(f"当前会话: {session.get('name', '未命名')}")
    print(f"使用搜索: {'是' if session.get('use_search', True) else '否'}, 使用思考: {'是' if session.get('use_thinking', False) else '否'}")
    print("="*50)
    print("输入 'q' 退出会话，输入 'menu' 显示会话内菜单")
    
    history = session.get('history', [])
    
    try:
        while True:
            content = input("\n请输入你想问的问题: ")
            
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
            response = send_message(
                token=token,
                session_id=session['id'], 
                content=content, 
                history=history,
                use_search=session.get('use_search', True),
                use_thinking=session.get('use_thinking', False)
            )
            
            # 如果发送失败
            if response is None:
                print("发送消息失败，请稍后再试")
                continue
            
            # 更新对话历史
            history.append({
                "user": content,
                "assistant": response["content"],
                "message_id": response["message_id"],
                "parent_message_id": response["parent_message_id"]
            })
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
    print("1. 开关搜索功能")
    print("2. 开关思考功能")
    print("3. 清空当前会话历史")
    print("4. 重命名会话")
    print("0. 返回对话")
    print("="*30)
    
    choice = input("请选择操作[0-4]: ")
    
    if choice == '1':
        # 开关搜索功能
        current = session.get('use_search', True)
        session['use_search'] = not current
        status = "开启" if session['use_search'] else "关闭"
        print(f"搜索功能已{status}")
        
    elif choice == '2':
        # 开关思考功能
        current = session.get('use_thinking', False)
        session['use_thinking'] = not current
        status = "开启" if session['use_thinking'] else "关闭"
        print(f"思考功能已{status}")
        
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

def main():
    global DEBUG, REQUEST_TIMEOUT
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='DeepSeek聊天机器人命令行客户端')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间(秒)')
    parser.add_argument('--token', type=str, help='DeepSeek API Token')
    args = parser.parse_args()
    
    # 设置调试模式
    DEBUG = args.debug
    if DEBUG:
        print("调试模式已启用")
    
    # 设置超时
    REQUEST_TIMEOUT = args.timeout
    
    # 获取token
    token = args.token
    if not token:
        token = input("请输入DeepSeek 认证 Token（自取）: ")
        if not token:
            print("Token不能为空，程序退出")
            return
    
    # 测试POW
    print("正在验证Token并测试PoW...")
    pow_response = get_pow_response(token)
    if not pow_response:
        print("获取PoW失败，请检查Token是否有效")
        return
    print("Token验证成功")
    
    # 加载所有会话
    sessions = load_sessions()
    
    # 主菜单循环
    try:
        while True:
            choice = show_menu()
            
            if choice == '0':
                print("\n感谢使用DeepSeek聊天机器人，再见！")
                break
                
            elif choice == '1':
                # 新建会话
                new_session = create_session_menu(token)
                if new_session:
                    sessions.append(new_session)
                    # 直接进入新会话的聊天模式
                    new_session = chat_mode(token, new_session)
                    # 保存所有会话
                    save_sessions(sessions)
                
            elif choice == '2':
                # 继续已有会话
                idx = select_session(sessions)
                if idx is not None:
                    session = sessions[idx]
                    # 进入聊天模式
                    session = chat_mode(token, session)
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
                print(f"默认选项已设置：使用搜索={'是' if defaults['use_search'] else '否'}, 使用思考={'是' if defaults['use_thinking'] else '否'}")
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