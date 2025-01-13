import os
from ..llm.symbol import SymbolProcessor
from openai import OpenAI
from ..utils.logger import logger
import dotenv
import time
import threading
from functools import wraps
from opencc import OpenCC

dotenv.load_dotenv()

def timeout_decorator(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            error = [None]
            completed = threading.Event()

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    error[0] = e
                finally:
                    completed.set()

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

            if completed.wait(seconds):
                if error[0] is not None:
                    raise error[0]
                return result[0]
            raise TimeoutError(f"操作超时 ({seconds}秒)")

        return wrapper
    return decorator

class WhisperProcessor:
    # 类级别的配置参数
    DEFAULT_TIMEOUT = 20  # API 超时时间（秒）
    DEFAULT_MODEL = "whisper-large-v3-turbo"
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        base_url = os.getenv("GROQ_BASE_URL")
        self.convert_to_simplified = os.getenv("CONVERT_TO_SIMPLIFIED", "false").lower() == "true"
        self.cc = OpenCC('t2s') if self.convert_to_simplified else None
        self.symbol = SymbolProcessor()
        self.add_symbol = os.getenv("ADD_SYMBOL", "false").lower() == "true"
        
        if not api_key:
            raise ValueError("未设置 GROQ_API_KEY 环境变量")
            
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        self.timeout_seconds = self.DEFAULT_TIMEOUT
    
    def _convert_traditional_to_simplified(self, text):
        """将繁体中文转换为简体中文"""
        if not self.convert_to_simplified or not text:
            return text
        return self.cc.convert(text)
    
    @timeout_decorator(20)
    def _call_api(self, mode, audio_data, prompt):
        """调用 Whisper API"""
        if mode == "translations":
            response = self.client.audio.translations.create(
                model="whisper-large-v3",
                response_format="text",
                prompt=prompt,
                file=("audio.wav", audio_data)
            )
        else:  # transcriptions
            response = self.client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                response_format="text",
                prompt=prompt,
                file=("audio.wav", audio_data)
            )
        return str(response).strip()
    
    def process_audio(self, audio_path, mode="transcriptions", prompt=""):
        """调用 Whisper API 处理音频（转录或翻译）
        
        Args:
            audio_path: 音频文件路径
            mode: 'transcriptions' 或 'translations'，决定是转录还是翻译
            prompt: 提示词
        
        Returns:
            tuple: (结果文本, 错误信息)
            - 如果成功，错误信息为 None
            - 如果失败，结果文本为 None
        """
        try:
            logger.info(f"正在调用 Whisper API... (模式: {mode})")
            start_time = time.time()
            
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
                result = self._call_api(mode, audio_data, prompt)
                logger.info(f"Whisper API 调用成功 ({mode}), 耗时: {time.time() - start_time:.1f}秒")
                result = self._convert_traditional_to_simplified(result)
                if self.add_symbol:
                    result = self.symbol.add_symbol(result)
                return result, None
                
        except TimeoutError:
            error_msg = f"❌ API 请求超时 ({self.timeout_seconds}秒)"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ {str(e)}"
            logger.error(f"音频处理错误: {str(e)}", exc_info=True)
            return None, error_msg
        finally:
            # 删除临时文件
            try:
                os.remove(audio_path)
                logger.info("临时音频文件已删除")
            except Exception as e:
                logger.error(f"删除临时文件失败: {e}") 