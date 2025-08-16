import os
import requests
from dotenv import load_dotenv
# from src.utils.logger import logger

load_dotenv()

class TranslateProcessor:
    def __init__(self):
        self.url = os.getenv("TRANSLATE_API_URL")
        assert self.url, "未设置 TRANSLATE_API_URL 环境变量"
        
        self.api_key = os.getenv("TRANSLATE_API_KEY")
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers['Authorization'] = f"Bearer {self.api_key}"
            
        self.model = os.getenv("TRANSLATE_MODEL")
        assert self.model, "未设置 TRANSLATE_MODEL 环境变量"

    def translate(self, text):
        system_prompt = """
        You are a translation assistant.
        Please translate the user's input into English.
        """

        payload = {
            "model": self.model,
            "messages":[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        }
        try:
            response = requests.request("POST", self.url, headers=self.headers, json=payload)
            # logger.info(f"调用翻译 API: {self.url}, model: {self.model}, 状态码: {response.status_code}, api_key: {self.api_key}")
            # logger.info(f"翻译 API 响应: {response.text}")
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            return text, e
