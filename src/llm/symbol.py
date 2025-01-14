from openai import OpenAI
import dotenv
import os
from ..utils.logger import logger

dotenv.load_dotenv()

class SymbolProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url=os.getenv("GROQ_BASE_URL"))
        self.model = os.getenv("GROQ_ADD_SYMBOL_MODEL", "llama3-8b-8192")

    def add_symbol(self, text):
        """为输入的文本添加合适的标点符号"""
        try:
            logger.info(f"正在添加标点符号...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                {"role": "system", "content": "Please add appropriate punctuation to the user’s input and return it. Apart from this, do not add or modify anything else."},
                {"role": "user", "content": text}
            ]
        )
            return response.choices[0].message.content
        except Exception as e:
            return text, e
        
    def optimize_result(self, text):
        """优化识别结果"""
        try:
            logger.info(f"正在添加标点符号...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                {"role": "system", "content": "Correct errors and add punctuation to the speech recognition input. If no changes are needed, output it directly. No explanation is required—just output."},
                {"role": "user", "content": text}
            ]
        )
            return response.choices[0].message.content
        except Exception as e:
            return text, e