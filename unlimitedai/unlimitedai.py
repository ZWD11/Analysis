import requests
import json
import uuid
import time
import sys
import os
from datetime import datetime, timezone

url = "https://app.unlimitedai.chat/?_rsc=1v2se"

payload = {}
headers = {
  'accept': '*/*',
  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(chat)%22%2C%7B%22children%22%3A%5B%22chat%22%2C%7B%22children%22%3A%5B%5B%22id%22%2C%22ad4d6aac-0a4e-4ec8-a81f-68e5f103d751%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2Fchat%2Fad4d6aac-0a4e-4ec8-a81f-68e5f103d751%22%2C%22refresh%22%5D%7D%5D%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
  'next-url': '/chat/ad4d6aac-0a4e-4ec8-a81f-68e5f103d751',
  'priority': 'u=1, i',
  'referer': 'https://app.unlimitedai.chat/chat/ad4d6aac-0a4e-4ec8-a81f-68e5f103d751',
  'rsc': '1',
  'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
  #'Cookie': '_ga=GA1.1.843752196.1744899840; __Host-authjs.csrf-token=cc80bab8a5e697593ceb466a38f5138f91f818b012a27fdacf315cc81d016a82%7C20fc88f54084fb5d7bf7b9fcea3925211a224ec00d944eca807085cd54d0e996; __Secure-authjs.callback-url=https%3A%2F%2Fapp.unlimitedai.chat; sidebar:state=false; _ga_BB7FNJV4KQ=GS1.1.1745670711.6.1.1745671249.0.0.0'
}

response = requests.request("GET", url, headers=headers, data=payload)

try:
    lines = response.text.strip().split('\n')
    for line in reversed(lines):
        if '"id":"' in line:
            start = line.find('"id":"') + 6
            end = line.find('"', start)
            if start != -1 and end != -1:
                chat_id = line[start:end]
                print(f"Chat ID: {chat_id}")
                break
    else:
        print("No ID found in the response")
except Exception as e:
    print(f"Error extracting ID: {e}")

message_history = []

def get_current_time():
    """生成当前时间的ISO格式字符串"""
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', '.000Z')

def extract_message_id(response_text):
    """从响应中提取消息ID"""
    for line in response_text.strip().split('\n'):
        if line.startswith('f:'):
            try:
                # f:{"messageId":"d0239faf-8326-4c0c-a537-747f48406eda"}
                json_str = line[2:]
                data = json.loads(json_str)
                return data.get('messageId')
            except:
                pass
    return None

def extract_bot_message(response_text):
    """从响应中提取AI回复的内容"""
    full_message = ""
    bot_reasoning = ""
    
    lines = response_text.strip().split('\n')
    
    # 提取推理内容
    for line in lines:
        if line.startswith('g:'):
            content = line[2:].strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            bot_reasoning += content
    
    # 提取回复内容
    for line in lines:
        if line.startswith('0:'):
            content = line[2:].strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            full_message += content
            
    return full_message, bot_reasoning

def save_conversation():
    """将对话历史保存到本地JSON文件"""
    if not os.path.exists('conversations'):
        os.makedirs('conversations')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversations/conversation_{chat_id}_{timestamp}.json"
    
    conversation_data = {
        "chat_id": chat_id,
        "timestamp": get_current_time(),
        "messages": message_history
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_conversation(filename):
    """从本地JSON文件加载对话历史"""
    global message_history
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
            message_history = conversation_data.get("messages", [])
        return True
    except Exception as e:
        print(f"加载对话历史失败: {e}")
        return False

def chat_with_bot():
    """与机器人进行对话"""
    global message_history
    
    load_option = input("是否加载已有对话？(y/n): ").lower()
    if load_option == 'y':
        if os.path.exists('conversations'):
            files = os.listdir('conversations')
            if files:
                print("\n可用的对话记录:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file}")
                try:
                    file_index = int(input("\n请选择要加载的对话编号: ")) - 1
                    if 0 <= file_index < len(files):
                        load_conversation(os.path.join('conversations', files[file_index]))
                        print(f"已加载对话，共 {len(message_history)} 条消息")
                    else:
                        print("无效的选择")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有找到保存的对话")
    
    while True:
        content = input("\n请输入内容 (输入 'exit' 退出, 'save' 保存对话): ")
        if content.lower() == 'exit':
            save_option = input("是否保存当前对话？(y/n): ").lower()
            if save_option == 'y':
                filename = save_conversation()
                print(f"对话已保存到: {filename}")
            break
        
        if content.lower() == 'save':
            filename = save_conversation()
            print(f"对话已保存到: {filename}")
            continue
            
        message_id = str(uuid.uuid4())
        current_time = get_current_time()
        
        user_message = {
            "id": message_id,
            "createdAt": current_time,
            "role": "user",
            "content": content,
            "parts": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        }
        
        message_history.append(user_message)
        
        payload = json.dumps({
            "id": chat_id,
            "messages": message_history,
            "selectedChatModel": "chat-model-reasoning"
        })
        
        chat_url = "https://app.unlimitedai.chat/api/chat"
        
        response = requests.post(chat_url, headers=headers, data=payload, stream=True)

        full_response = ""
        accumulated_response = ""
        
        print("\nAI正在回复: ", end="", flush=True)
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                full_response += decoded_line + "\n"
                
                if decoded_line.startswith('0:'):
                    content_chunk = decoded_line[2:].strip()
                    
                    if content_chunk.startswith('"') and content_chunk.endswith('"'):
                        content_chunk = content_chunk[1:-1]
                    
                    sys.stdout.write(content_chunk)
                    sys.stdout.flush()
                    accumulated_response += content_chunk
                    
                    time.sleep(0.03)
        
        print("\n")
        
        bot_message_text, bot_reasoning = extract_bot_message(full_response)
        bot_message_id = extract_message_id(full_response)
        
        if bot_message_id:
            bot_message = {
                "id": bot_message_id,
                "createdAt": get_current_time(),
                "role": "assistant",
                "content": bot_message_text,
                "parts": [
                    {
                        "type": "step-start"
                    },
                    {
                        "type": "reasoning",
                        "reasoning": bot_reasoning,
                        "details": [
                            {
                                "type": "text",
                                "text": bot_reasoning
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": bot_message_text
                    }
                ],
                "reasoning": bot_reasoning,
                "revisionId": str(uuid.uuid4())
            }
            
            message_history.append(bot_message)
            
            # 每次收到回复后自动保存对话（可选功能）
            # auto_save_file = save_conversation()
            # print(f"对话已自动保存到: {auto_save_file}")
        
        # 保存完整响应到文件（调试用）
        with open("response_log.txt", "w", encoding="utf-8") as f:
            f.write(full_response)

print("\n欢迎使用 UnlimitedAI.Chat！开始对话吧！")
chat_with_bot()

