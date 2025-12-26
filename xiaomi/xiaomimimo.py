import requests
import json
import secrets
import time
import sys
import os
import re
import urllib.parse
from datetime import datetime

class XiaomiChat:
    def __init__(self):
        self.base_url = "https://aistudio.xiaomimimo.com"
        self.conversation_id = None
        self.current_conversation = None
        self.conversations_file = "conversations.json"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'system',
            'content-type': 'application/json',
            'origin': self.base_url,
            'priority': 'u=1, i',
            'referer': f'{self.base_url}/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'x-timezone': 'Asia/Shanghai',
            'Cookie': 'serviceToken="/vjQa88K2J......."' #你的cookie
        }
        self.ph_token = self._extract_ph_token()
        self.load_conversations()
    
    def _extract_ph_token(self):
        """从 Cookie 中提取 xiaomichatbot_ph 值"""
        cookie_str = self.headers.get('Cookie', '')
        match = re.search(r'xiaomichatbot_ph=(?:"([^"]+)"|([^;]+))', cookie_str)
        if match:
            token = match.group(1) or match.group(2)
            return token.strip()
        return ""
    
    def load_conversations(self):
        """从本地加载对话历史"""
        if os.path.exists(self.conversations_file):
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except:
                self.conversations = {}
        else:
            self.conversations = {}
    
    def save_conversations(self):
        """保存对话历史到本地"""
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)
    
    def create_conversation(self):
        """创建新对话"""
        url = f"{self.base_url}/open-apis/chat/conversation/save?xiaomichatbot_ph={urllib.parse.quote(self.ph_token)}"
        hex_str = secrets.token_hex(16)
        
        payload = json.dumps({
            "conversationId": hex_str,
            "title": "新对话",
            "type": "chat"
        })
        
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_data = response.json()
            self.conversation_id = response_data['data']['conversationId']
            
            # 保存到本地
            self.current_conversation = {
                'id': self.conversation_id,
                'title': '新对话',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'messages': []
            }
            self.conversations[self.conversation_id] = self.current_conversation
            self.save_conversations()
            
            print(f"\n✓ 已创建新对话，对话ID: {self.conversation_id}\n")
            return True
        except Exception as e:
            print(f"✗ 创建对话失败: {e}")
            return False
    
    def gen_title(self, content):
        """生成对话标题"""
        url = f"{self.base_url}/open-apis/chat/conversation/genTitle?xiaomichatbot_ph={urllib.parse.quote(self.ph_token)}"
        payload = json.dumps({"content": content})
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
        except:
            pass
        return None

    def update_conversation_title(self, title):
        """更新对话标题（本地和远程）"""
        if not self.conversation_id:
            return
        
        url = f"{self.base_url}/open-apis/chat/conversation/save?xiaomichatbot_ph={urllib.parse.quote(self.ph_token)}"
        payload = json.dumps({
            "conversationId": self.conversation_id,
            "title": title,
            "type": "chat"
        })
        
        try:
            requests.post(url, headers=self.headers, data=payload)
            self.current_conversation['title'] = title
            self.save_conversations()
            print(f"✓ 对话标题已更新为: {title}")
        except Exception as e:
            print(f"✗ 更新标题失败: {e}")

    def generate_msg_id(self):
        """生成消息ID"""
        timestamp = int(time.time() * 1000)
        time_part = ''
        base36 = '0123456789abcdefghijklmnopqrstuvwxyz'
        while timestamp > 0:
            timestamp, remainder = divmod(timestamp, 36)
            time_part = base36[remainder] + time_part
        time_part = time_part.zfill(8)[:8]
        random_part = secrets.token_hex(12)
        return time_part + random_part
    
    def send_message(self, query):
        """发送消息并处理流式响应"""
        if not self.conversation_id:
            print("✗ 请先选择或创建对话")
            return
        
        url = f"{self.base_url}/open-apis/bot/chat?xiaomichatbot_ph={urllib.parse.quote(self.ph_token)}"
        msg_id = self.generate_msg_id()
        
        payload = json.dumps({
            "msgId": msg_id,
            "conversationId": self.conversation_id,
            "query": query,
            "modelConfig": {
                "enableThinking": True,
                "temperature": 0.8,
                "topP": 0.95,
                "webSearchStatus": "disabled",
                "model": "mimo-v2-flash-studio"
            },
            "multiMedias": []
        })
        
        # 保存用户消息
        user_message = {
            'role': 'user',
            'content': query,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.current_conversation['messages'].append(user_message)
        
        try:
            response = requests.post(url, headers=self.headers, data=payload, stream=True)
            
            thinking_content = ""
            normal_content = ""
            in_thinking = False
            buffer = ""
            
            print("AI: ", end='', flush=True)
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        data_str = line[5:].strip()
                        if data_str and data_str != '[DONE]':
                            try:
                                data = json.loads(data_str)
                                if isinstance(data, dict):
                                    if data.get('type') == 'text':
                                        content = data.get('content', '')
                                        if not content:
                                            continue
                                        
                                        # 处理 \u0000 等特殊字符
                                        content = content.replace('\u0000', '')
                                        
                                        # 处理 thinking 标签
                                        while content:
                                            if in_thinking:
                                                if '</think>' in content:
                                                    parts = content.split('</think>', 1)
                                                    thinking_part = parts[0]
                                                    if thinking_part:
                                                        thinking_content += thinking_part
                                                        print(thinking_part, end='', flush=True)
                                                    
                                                    in_thinking = False
                                                    print("\n\n[回复内容] ", end='', flush=True)
                                                    content = parts[1]
                                                else:
                                                    thinking_content += content
                                                    print(content, end='', flush=True)
                                                    content = ""
                                            else:
                                                if '<think>' in content:
                                                    parts = content.split('<think>', 1)
                                                    normal_part = parts[0]
                                                    if normal_part:
                                                        normal_content += normal_part
                                                        print(normal_part, end='', flush=True)
                                                    
                                                    in_thinking = True
                                                    print("\n\n[思考过程] ", end='', flush=True)
                                                    content = parts[1]
                                                else:
                                                    normal_content += content
                                                    print(content, end='', flush=True)
                                                    content = ""
                                elif isinstance(data, list):
                                    # 处理搜索结果等列表类型数据，目前直接跳过或可根据需要打印
                                    pass
                            except json.JSONDecodeError:
                                pass
                    elif line.startswith('event:finish'):
                        break
            
            print("\n")
            
            # 保存AI回复
            ai_message = {
                'role': 'assistant',
                'content': normal_content,
                'thinking': thinking_content if thinking_content else None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.current_conversation['messages'].append(ai_message)
            self.save_conversations()
            
            # 如果是第一轮对话且标题仍为"新对话"，则生成并更新标题
            if len(self.current_conversation['messages']) == 2 and self.current_conversation.get('title') == "新对话":
                title_content = f"{query} {normal_content}"
                new_title = self.gen_title(title_content)
                if new_title:
                    self.update_conversation_title(new_title)
            
        except Exception as e:
            print(f"\n✗ 发送消息失败: {e}")
            import traceback
            traceback.print_exc()
    
    def list_conversations(self):
        """列出所有对话"""
        if not self.conversations:
            print("\n暂无对话记录\n")
            return
        
        print("\n" + "=" * 60)
        print("对话列表")
        print("=" * 60)
        
        conv_list = list(self.conversations.items())
        for idx, (conv_id, conv) in enumerate(conv_list, 1):
            msg_count = len(conv['messages'])
            print(f"{idx}. [{conv['created_at']}] {conv['title']} ({msg_count}条消息)")
            print(f"   ID: {conv_id}")
        
        print("=" * 60 + "\n")
        return conv_list
    
    def view_conversation(self, conv_id):
        """查看特定对话的内容"""
        if conv_id not in self.conversations:
            print("✗ 对话不存在")
            return False
        
        self.current_conversation = self.conversations[conv_id]
        self.conversation_id = conv_id
        
        print("\n" + "=" * 60)
        print(f"对话: {self.current_conversation['title']}")
        print(f"创建时间: {self.current_conversation['created_at']}")
        print("=" * 60 + "\n")
        
        for msg in self.current_conversation['messages']:
            if msg['role'] == 'user':
                print(f"你 [{msg['timestamp']}]: {msg['content']}")
            else:
                if msg.get('thinking'):
                    print(f"\nAI [{msg['timestamp']}]:")
                    print(f"[思考过程] {msg['thinking']}")
                    print(f"[回复内容] {msg['content']}")
                else:
                    print(f"\nAI [{msg['timestamp']}]: {msg['content']}")
            print()
        
        return True
    
    def main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "=" * 60)
            print("小米AI对话助手")
            print("=" * 60)
            print("1. 新建对话")
            print("2. 查看对话列表")
            print("3. 退出程序")
            print("=" * 60)
            
            choice = input("\n请选择操作 (1-3): ").strip()
            
            if choice == '1':
                if self.create_conversation():
                    self.chat_loop()
            
            elif choice == '2':
                conv_list = self.list_conversations()
                if conv_list:
                    try:
                        idx = int(input("请选择对话编号 (输入0返回): ").strip())
                        if idx == 0:
                            continue
                        if 1 <= idx <= len(conv_list):
                            conv_id = conv_list[idx - 1][0]
                            if self.view_conversation(conv_id):
                                self.chat_loop()
                        else:
                            print("✗ 无效的编号")
                    except ValueError:
                        print("✗ 请输入数字")
            
            elif choice == '3':
                print("\n再见！")
                break
            
            else:
                print("✗ 无效的选择")
    
    def chat_loop(self):
        """对话循环"""
        print("\n提示: 输入 'back' 返回主菜单，输入 'quit' 退出程序\n")
        
        while True:
            try:
                user_input = input("你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n再见！")
                    sys.exit(0)
                
                if user_input.lower() in ['back', '返回']:
                    break
                
                self.send_message(user_input)
                
            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                print(f"\n发生错误: {e}")

if __name__ == "__main__":
    chat = XiaomiChat()
    chat.main_menu()