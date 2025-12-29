import time
import hashlib
import json
import hmac
import base64
import requests
import threading
import re
import os
import uuid
import io
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
from typing import Tuple, Optional, Generator, List, Dict

CONVERSATIONS_FILE = "conversations.json"

class GeminiJWTAuth:
    def __init__(self, csesidx: str, cookie: str):
        self.csesidx = csesidx
        self.cookie = cookie
        self.base_url = "https://business.gemini.google"
        self.jwt_token = None
        self.last_refresh_time = 0
        self._lock = threading.Lock()

    def _url_safe_b64encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    def _kq_encode(self, s: str) -> str:
        byte_arr = bytearray()
        for char in s:
            val = ord(char)
            if val > 255:
                byte_arr.append(val & 255)
                byte_arr.append(val >> 8)
            else:
                byte_arr.append(val)
        return self._url_safe_b64encode(bytes(byte_arr))

    def _decode_xsrf_token(self, xsrf_token: str) -> bytes:
        padding = 4 - len(xsrf_token) % 4
        if padding != 4:
            xsrf_token += '=' * padding
        return base64.urlsafe_b64decode(xsrf_token)

    def _get_token(self) -> Tuple[str, str]:
        url = f"{self.base_url}/auth/getoxsrf?csesidx={self.csesidx}"
        headers = {
            'accept': '*/*',
            'referer': f'{self.base_url}/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Cookie': self.cookie
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_text = response.text
        if response_text.startswith(")]}'"):
            response_text = response_text[4:]
        data = json.loads(response_text)
        return data.get("xsrfToken"), data.get("keyId")

    def _create_jwt(self, key_bytes: bytes, key_id: str) -> str:
        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT", "kid": key_id}
        payload = {
            "iss": self.base_url,
            "aud": "https://biz-discoveryengine.googleapis.com",
            "sub": f"csesidx/{self.csesidx}",
            "iat": now, "exp": now + 300, "nbf": now
        }
        header_b64 = self._kq_encode(json.dumps(header, separators=(',', ':')))
        payload_b64 = self._kq_encode(json.dumps(payload, separators=(',', ':')))
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(key_bytes, message.encode('utf-8'), hashlib.sha256).digest()
        return f"{message}.{self._url_safe_b64encode(signature)}"

    def refresh_jwt(self):
        with self._lock:
            xsrf_token, key_id = self._get_token()
            key_bytes = self._decode_xsrf_token(xsrf_token)
            self.jwt_token = self._create_jwt(key_bytes, key_id)
            self.last_refresh_time = time.time()

    def get_token(self) -> str:
        if not self.jwt_token or (time.time() - self.last_refresh_time) > 240:
            self.refresh_jwt()
        return self.jwt_token


class ConversationManager:
    def __init__(self, file_path: str = CONVERSATIONS_FILE):
        self.file_path = file_path
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {"conversations": {}}

    def _save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def create_conversation(self, session_name: str, title: str = "") -> str:
        conv_id = str(uuid.uuid4())[:8]
        self.data["conversations"][conv_id] = {
            "id": conv_id,
            "session_name": session_name,
            "title": title or f"对话 {conv_id}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self._save()
        return conv_id

    def add_message(self, conv_id: str, role: str, content: str):
        if conv_id in self.data["conversations"]:
            self.data["conversations"][conv_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.data["conversations"][conv_id]["updated_at"] = datetime.now().isoformat()
            if role == "user" and not self.data["conversations"][conv_id]["messages"][0]["content"]:
                self.data["conversations"][conv_id]["title"] = content[:30] + ("..." if len(content) > 30 else "")
            self._save()

    def update_title(self, conv_id: str, title: str):
        if conv_id in self.data["conversations"]:
            self.data["conversations"][conv_id]["title"] = title
            self._save()

    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        return self.data["conversations"].get(conv_id)

    def get_conversation_by_session(self, session_name: str) -> Optional[Dict]:
        for conv in self.data["conversations"].values():
            if conv["session_name"] == session_name:
                return conv
        return None

    def list_conversations(self) -> List[Dict]:
        convs = list(self.data["conversations"].values())
        convs.sort(key=lambda x: x["updated_at"], reverse=True)
        return convs

    def delete_conversation(self, conv_id: str) -> bool:
        if conv_id in self.data["conversations"]:
            del self.data["conversations"][conv_id]
            self._save()
            return True
        return False


class GeminiClient:
    def __init__(self, csesidx: str, cookie: str, config_id: str = "你的config_id"):
        self.auth = GeminiJWTAuth(csesidx, cookie)
        self.config_id = config_id
        self.session_name = None
        self.base_api_url = "https://biz-discoveryengine.googleapis.com/v1alpha/locations/global"
        self.conv_manager = ConversationManager()
        self.current_conv_id = None

    def _get_headers(self):
        return {
            'accept': '*/*',
            'authorization': f'Bearer {self.auth.get_token()}',
            'content-type': 'application/json',
            'origin': 'https://business.gemini.google',
            'referer': 'https://business.gemini.google/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }

    def create_session(self):
        url = f"{self.base_api_url}/widgetCreateSession"
        payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "createSessionRequest": {"session": {"name": "-", "displayName": ""}}
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        self.session_name = response.json()["session"]["name"]
        self.current_conv_id = self.conv_manager.create_conversation(self.session_name)
        return self.session_name

    def load_conversation(self, conv_id: str) -> bool:
        conv = self.conv_manager.get_conversation(conv_id)
        if conv:
            self.session_name = conv["session_name"]
            self.current_conv_id = conv_id
            return True
        return False

    def stream_chat(self, text: str, session_name: Optional[str] = None, include_thought: bool = False) -> Generator[Tuple[str, bool], None, None]:
        if session_name:
            self.session_name = session_name
            conv = self.conv_manager.get_conversation_by_session(session_name)
            if conv:
                self.current_conv_id = conv["id"]
        elif not self.session_name:
            self.create_session()

        if self.current_conv_id:
            self.conv_manager.add_message(self.current_conv_id, "user", text)

        url = f"{self.base_api_url}/widgetStreamAssist"
        payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "streamAssistRequest": {
                "session": self.session_name,
                "query": {"parts": [{"text": text}]},
                "answerGenerationMode": "NORMAL",
                "languageCode": "zh-CN",
                "userMetadata": {"timeZone": "Asia/Shanghai"},
                "assistSkippingMode": "REQUEST_ASSIST"
            }
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload, stream=True, timeout=120)
        response.raise_for_status()
        
        text_pattern = re.compile(r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"')
        thought_pattern = re.compile(r'"thought"\s*:\s*true')
        
        output_texts = []
        buffer = ""
        full_response = ""
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                if isinstance(line, bytes):
                    line = line.decode('utf-8', errors='replace')
                buffer += line
                
                for match in text_pattern.finditer(buffer):
                    text_content = match.group(1)
                    
                    if text_content in output_texts:
                        continue
                    output_texts.append(text_content)
                    
                    try:
                        decoded_text = json.loads(f'"{text_content}"')
                    except:
                        decoded_text = text_content
                    
                    match_start = match.start()
                    context_start = max(0, match_start - 50)
                    context = buffer[context_start:match_start + len(match.group(0)) + 50]
                    is_thought = bool(thought_pattern.search(context))
                    
                    if is_thought:
                        if include_thought:
                            yield (decoded_text, True)
                    else:
                        full_response += decoded_text
                        yield (decoded_text, False)
        
        if self.current_conv_id and full_response:
            self.conv_manager.add_message(self.current_conv_id, "assistant", full_response)

    def list_conversations(self) -> List[Dict]:
        return self.conv_manager.list_conversations()

    def show_conversation(self, conv_id: str) -> Optional[Dict]:
        return self.conv_manager.get_conversation(conv_id)

    def delete_conversation(self, conv_id: str) -> bool:
        return self.conv_manager.delete_conversation(conv_id)

    def generate_image(self, prompt: str):
        if not self.session_name:
            self.create_session()
            
        print(f"正在生成图片: {prompt}...")
        
        # 1. 调用 widgetStreamAssist
        url = f"{self.base_api_url}/widgetStreamAssist"
        payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "streamAssistRequest": {
                "session": self.session_name,
                "query": {"parts": [{"text": prompt}]},
                "answerGenerationMode": "NORMAL",
                "toolsSpec": {"imageGenerationSpec": {}},
                "languageCode": "zh-CN",
                "userMetadata": {"timeZone": "Asia/Shanghai"},
                "assistSkippingMode": "REQUEST_ASSIST"
            }
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        
        # 2. 调用 widgetListSessionFileMetadata 获取文件列表
        metadata_url = f"{self.base_api_url}/widgetListSessionFileMetadata"
        metadata_payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "listSessionFileMetadataRequest": {
                "name": self.session_name,
                "filter": "file_origin_type = AI_GENERATED"
            }
        }
        
        metadata_response = requests.post(metadata_url, headers=self._get_headers(), json=metadata_payload)
        metadata_response.raise_for_status()
        metadata_data = metadata_response.json()
        
        files = metadata_data.get("listSessionFileMetadataResponse", {}).get("fileMetadata", [])
        if not files:
            print("未能找到生成的图片文件。")
            return
            
        # 获取最新的一个文件
        latest_file = files[0] # metadata 通常返回最新的在前面
        download_uri = latest_file.get("downloadUri")
        if not download_uri:
            print("未能获取下载链接。")
            return
            
        final_url = download_uri.replace("https://discoveryengine.googleapis.com/v1/", "https://biz-discoveryengine.googleapis.com/download/v1alpha/")
        final_url = final_url.replace("file_id=", "fileId=")
        
        # 4. 下载并获取 base64
        download_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {self.auth.get_token()}',
            'content-type': 'application/json',
            'origin': 'https://business.gemini.google',
            'referer': 'https://business.gemini.google/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-goog-encode-response-if-executable': 'base64'
        }
        
        img_response = requests.get(final_url, headers=download_headers)
        img_response.raise_for_status()
        
        base64_content = img_response.text.strip()
        
        # 5. 保存到对话记录
        if self.current_conv_id:
            self.conv_manager.add_message(self.current_conv_id, "user", f"img {prompt}")
            self.conv_manager.add_message(self.current_conv_id, "assistant", f"image_base64:{base64_content}")

        # 6. 显示图片
        self._show_image_window(base64_content)

    def _show_image_window(self, base64_data):
        try:
            base64_data = base64_data.strip()
            image_data = base64.b64decode(base64_data)
            
            def show():
                root = tk.Tk()
                root.title("Generated Image")
                
                img = Image.open(io.BytesIO(image_data))
                
                max_w, max_h = 1024, 768
                w, h = img.size
                if w > max_w or h > max_h:
                    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(root, image=photo)
                label.pack()
                label.image = photo
                root.mainloop()
            
            threading.Thread(target=show, daemon=True).start()
            print("[图片窗口已弹出]")
        except Exception as e:
            print(f"[显示图片失败: {e}]")

    def generate_video(self, prompt: str):
        if not self.session_name:
            self.create_session()
            
        print(f"正在生成视频: {prompt}...")
        print("(视频生成可能需要较长时间，请耐心等待...)")
        
        url = f"{self.base_api_url}/widgetStreamAssist"
        payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "streamAssistRequest": {
                "session": self.session_name,
                "query": {"parts": [{"text": prompt}]},
                "filter": "",
                "fileIds": [],
                "answerGenerationMode": "NORMAL",
                "toolsSpec": {"videoGenerationSpec": {}},
                "languageCode": "zh-CN",
                "userMetadata": {"timeZone": "Asia/Shanghai"},
                "assistSkippingMode": "REQUEST_ASSIST"
            }
        }
        
        headers = self._get_headers()
        headers['x-server-timeout'] = '1800'
        
        response = requests.post(url, headers=headers, json=payload, timeout=1800)
        response.raise_for_status()
        
        metadata_url = f"{self.base_api_url}/widgetListSessionFileMetadata"
        metadata_payload = {
            "configId": self.config_id,
            "additionalParams": {"token": "-"},
            "listSessionFileMetadataRequest": {
                "name": self.session_name,
                "filter": "file_origin_type = AI_GENERATED"
            }
        }
        
        metadata_response = requests.post(metadata_url, headers=self._get_headers(), json=metadata_payload)
        metadata_response.raise_for_status()
        metadata_data = metadata_response.json()
        
        files = metadata_data.get("listSessionFileMetadataResponse", {}).get("fileMetadata", [])
        video_file = None
        for f in files:
            if f.get("mimeType", "").startswith("video/"):
                video_file = f
                break
        
        if not video_file:
            print("未能找到生成的视频文件。")
            return
            
        download_uri = video_file.get("downloadUri")
        if not download_uri:
            print("未能获取下载链接。")
            return
            
        final_url = download_uri.replace("https://discoveryengine.googleapis.com/v1/", "https://biz-discoveryengine.googleapis.com/download/v1alpha/")
        final_url = final_url.replace("file_id=", "fileId=")
        
        download_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {self.auth.get_token()}',
            'content-type': 'application/json',
            'origin': 'https://business.gemini.google',
            'referer': 'https://business.gemini.google/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-goog-encode-response-if-executable': 'base64'
        }
        
        video_response = requests.get(final_url, headers=download_headers, timeout=300)
        video_response.raise_for_status()
        
        base64_content = video_response.text.strip()
        
        if self.current_conv_id:
            self.conv_manager.add_message(self.current_conv_id, "user", f"video {prompt}")
            self.conv_manager.add_message(self.current_conv_id, "assistant", f"video_base64:{base64_content}")
        
        self._show_video_window(base64_content)

    def _show_video_window(self, base64_data):
        try:
            import tempfile
            import subprocess
            import os as os_module
            
            base64_data = base64_data.strip()
            video_data = base64.b64decode(base64_data)
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_file.write(video_data)
            temp_file.close()
            
            print(f"[视频已保存到临时文件: {temp_file.name}]")
            
            if os_module.name == 'nt':
                os_module.startfile(temp_file.name)
            elif os_module.name == 'posix':
                subprocess.Popen(['xdg-open', temp_file.name])
            else:
                subprocess.Popen(['open', temp_file.name])
            
            print("[视频播放器已启动]")
        except Exception as e:
            print(f"[显示视频失败: {e}]")

    def chat_loop(self, include_thought: bool = False):
        print("=" * 50)
        print("Gemini 对话模式")
        print("=" * 50)
        print("命令:")
        print("  exit          - 退出")
        print("  new           - 开启新对话")
        print("  img <prompt>  - 图片生成")
        print("  video <prompt>- 视频生成")
        print("  list          - 查看对话列表")
        print("  load <id>     - 继续指定对话")
        print("  show <id>     - 查看对话详情")
        print("  del <id>      - 删除对话")
        print("  rename <title>- 重命名当前对话")
        print("=" * 50)
        
        while True:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() == 'exit':
                break
                
            if user_input.lower() == 'new':
                self.session_name = None
                self.current_conv_id = None
                self.create_session()
                print("--- 已开启新对话 ---")
                continue

            if user_input.lower().startswith('img '):
                prompt = user_input[4:].strip()
                try:
                    self.generate_image(prompt)
                except Exception as e:
                    print(f"[图片生成失败: {e}]")
                continue

            if user_input.lower().startswith('video '):
                prompt = user_input[6:].strip()
                try:
                    self.generate_video(prompt)
                except Exception as e:
                    print(f"[视频生成失败: {e}]")
                continue
                
            if user_input.lower() == 'list':
                convs = self.list_conversations()
                if not convs:
                    print("暂无对话记录")
                else:
                    print("\n对话列表:")
                    print("-" * 60)
                    for conv in convs:
                        msg_count = len(conv["messages"])
                        updated = conv["updated_at"][:19].replace("T", " ")
                        current = " *" if conv["id"] == self.current_conv_id else ""
                        print(f"  [{conv['id']}] {conv['title']} ({msg_count}条消息, {updated}){current}")
                    print("-" * 60)
                continue
                
            if user_input.lower().startswith('load '):
                conv_id = user_input[5:].strip()
                if self.load_conversation(conv_id):
                    conv = self.show_conversation(conv_id)
                    print(f"\n{'=' * 50}")
                    print(f"已加载对话: {conv['title']}")
                    print(f"创建时间: {conv['created_at'][:19].replace('T', ' ')}")
                    print(f"{'=' * 50}")
                    if conv["messages"]:
                        print("\n历史消息:")
                        print("-" * 50)
                        for msg in conv["messages"]:
                            role = "User" if msg["role"] == "user" else "Gemini"
                            content = msg["content"]
                            if content.startswith("image_base64:"):
                                content = "[图片数据 (Base64)]"
                            elif content.startswith("video_base64:"):
                                content = "[视频数据 (Base64)]"
                            print(f"\n{role}:")
                            print(content)
                        print("-" * 50)
                    print("\n可以继续对话了")
                else:
                    print(f"未找到对话: {conv_id}")
                continue
                
            if user_input.lower().startswith('show '):
                conv_id = user_input[5:].strip()
                conv = self.show_conversation(conv_id)
                if conv:
                    print(f"\n对话: {conv['title']}")
                    print(f"创建时间: {conv['created_at'][:19].replace('T', ' ')}")
                    print("-" * 40)
                    for msg in conv["messages"]:
                        role = "User" if msg["role"] == "user" else "Gemini"
                        content = msg["content"]
                        if content.startswith("image_base64:"):
                            content = "[图片数据 (Base64)]"
                        elif content.startswith("video_base64:"):
                            content = "[视频数据 (Base64)]"
                        else:
                            content = content[:100] + "..." if len(content) > 100 else content
                        print(f"{role}: {content}")
                    print("-" * 40)
                else:
                    print(f"未找到对话: {conv_id}")
                continue
                
            if user_input.lower().startswith('del '):
                conv_id = user_input[4:].strip()
                if self.delete_conversation(conv_id):
                    print(f"已删除对话: {conv_id}")
                    if conv_id == self.current_conv_id:
                        self.session_name = None
                        self.current_conv_id = None
                else:
                    print(f"未找到对话: {conv_id}")
                continue
                
            if user_input.lower().startswith('rename '):
                new_title = user_input[7:].strip()
                if self.current_conv_id:
                    self.conv_manager.update_title(self.current_conv_id, new_title)
                    print(f"已重命名为: {new_title}")
                else:
                    print("当前没有活动对话")
                continue

            print("Gemini: ", end="", flush=True)
            try:
                for text, is_thought in self.stream_chat(user_input, include_thought=include_thought):
                    if is_thought:
                        print(f"\n[Thought]: {text}", end="", flush=True)
                    else:
                        print(text, end="", flush=True)
            except Exception as e:
                print(f"\n[错误: {e}]")
            print()


if __name__ == "__main__":
    CSESIDX = "你的设备码"
    COOKIE = "你的cookie" #还有大概161行的config_id需要填入

    client = GeminiClient(CSESIDX, COOKIE)
    client.chat_loop(include_thought=True)
