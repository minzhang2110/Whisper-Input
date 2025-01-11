import sounddevice as sd
import numpy as np
import pyperclip
from pynput.keyboard import Controller, Key, Listener
import queue
from groq import Groq
import sys
import os
import tempfile
import soundfile as sf
import logging
import colorlog
import dotenv

dotenv.load_dotenv()

# 配置彩色日志
def setup_logger():
    """配置彩色日志"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt='%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING': 'yellow',
            'ERROR':   'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    ))
    
    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # 移除可能存在的默认处理器
    for handler in logger.handlers[:-1]:
        logger.removeHandler(handler)
    
    return logger

logger = setup_logger()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def check_accessibility_permissions():
    """检查是否有辅助功能权限并提供指导"""
    logger.warning("\n=== macOS 辅助功能权限检查 ===")
    logger.warning("此应用需要辅助功能权限才能监听键盘事件。")
    logger.warning("\n请按照以下步骤授予权限：")
    logger.warning("1. 打开 系统偏好设置")
    logger.warning("2. 点击 隐私与安全性")
    logger.warning("3. 点击左侧的 辅助功能")
    logger.warning("4. 点击右下角的锁图标并输入密码")
    logger.warning("5. 在右侧列表中找到 Terminal（或者您使用的终端应用）并勾选")
    logger.warning("\n授权后，请重新运行此程序。")
    logger.warning("===============================\n")

class VoiceInputTool:
    def __init__(self):
        self.keyboard = Controller()
        self.recording = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.option_pressed = False
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"初始化完成，临时文件目录: {self.temp_dir}")
        
    def start_recording(self):
        """开始录音"""
        if not self.recording:
            logger.info("开始录音...")
            self.recording = True
            self.audio_data = []
            
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"音频录制状态: {status}")
                if self.recording:
                    self.audio_queue.put(indata.copy())
            
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback
            )
            self.stream.start()
            logger.info("音频流已启动")
    
    def stop_recording(self):
        """停止录音并处理音频"""
        if self.recording:
            logger.info("停止录音...")
            self.recording = False
            self.stream.stop()
            self.stream.close()
            
            # 收集所有音频数据
            audio_data = []
            logger.info("处理录音数据...")
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())
            
            if audio_data:
                # 合并音频数据
                audio = np.concatenate(audio_data)
                logger.info(f"音频数据长度: {len(audio)} 采样点")
                
                # 保存为临时文件
                temp_path = os.path.join(self.temp_dir, "temp_audio.wav")
                sf.write(temp_path, audio, self.sample_rate)
                logger.info(f"音频已保存到临时文件: {temp_path}")
                
                # 调用语音识别API
                logger.info("开始转录音频...")
                text = self.transcribe_audio(temp_path)
                
                # 删除临时文件
                try:
                    os.remove(temp_path)
                    logger.info("临时音频文件已删除")
                except Exception as e:
                    logger.error(f"删除临时文件失败: {e}")
                
                # 输出文字到当前光标位置
                if text:
                    logger.info(f"转录结果: {text}")
                    self.type_text(text)
                else:
                    logger.warning("未获得转录结果")
            else:
                logger.warning("没有收集到音频数据")
    
    def transcribe_audio(self, audio_path):
        """调用 Whisper API 转录音频"""
        try:
            logger.info("正在调用 Whisper API...")
            with open(audio_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo", 
                    response_format="text",
                    prompt="适当添加标点符号",
                    file=("audio.wav", audio_file.read())
                )
                result = str(response).strip()
                logger.info("Whisper API 调用成功")
                return result
        except Exception as e:
            logger.error(f"转录错误: {str(e)}", exc_info=True)
            return f"转录失败: {str(e)}"
    
    def type_text(self, text):
        """将文字输入到当前光标位置"""
        try:
            logger.info("正在输入转录文本...")
            pyperclip.copy(text)
            # 模拟Command+V
            with self.keyboard.pressed(Key.cmd):
                self.keyboard.press('v')
                self.keyboard.release('v')
            logger.info("文本输入完成")
        except Exception as e:
            logger.error(f"文本输入失败: {e}")

    def on_press(self, key):
        """按键按下时的回调"""
        if key == Key.alt_l:  # alt_l 是左 Option 键
            logger.debug("检测到 Option 键按下")
            self.option_pressed = True
            self.start_recording()

    def on_release(self, key):
        """按键释放时的回调"""
        if key == Key.alt_l:
            logger.debug("检测到 Option 键释放")
            self.option_pressed = False
            self.stop_recording()

    def __del__(self):
        """清理临时文件夹"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("临时目录已清理")
        except Exception as e:
            logger.error(f"清理临时目录失败: {e}")

def main():
    try:
        tool = VoiceInputTool()
        logger.info("=== 语音输入工具已启动 ===")
        logger.info("按住 Option 键开始录音，松开结束录音")
        
        # 创建键盘监听器
        with Listener(on_press=tool.on_press, on_release=tool.on_release) as listener:
            listener.join()
    except Exception as e:
        if "Input event monitoring will not be possible" in str(e):
            check_accessibility_permissions()
            sys.exit(1)
        else:
            logger.error(f"发生错误: {str(e)}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    main()