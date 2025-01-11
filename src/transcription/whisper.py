import os
from groq import Groq
from ..utils.logger import logger
import dotenv

dotenv.load_dotenv()

class WhisperTranscriber:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def transcribe(self, audio_path):
        """调用 Whisper API 转录音频"""
        try:
            logger.info("正在调用 Whisper API...")
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo", 
                    response_format="text",
                    prompt="适当添加标点符号，通常是简体中文",
                    file=("audio.wav", audio_file.read())
                )
                result = str(response).strip()
                logger.info("Whisper API 调用成功")
                return result
        except Exception as e:
            logger.error(f"转录错误: {str(e)}", exc_info=True)
            return None
        finally:
            # 删除临时文件
            try:
                os.remove(audio_path)
                logger.info("临时音频文件已删除")
            except Exception as e:
                logger.error(f"删除临时文件失败: {e}") 