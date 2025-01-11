import sys
from src.audio.recorder import AudioRecorder
from src.keyboard.listener import KeyboardManager, check_accessibility_permissions
from src.transcription.whisper import WhisperProcessor
from src.utils.logger import logger

def check_microphone_permissions():
    """检查麦克风权限并提供指导"""
    logger.warning("\n=== macOS 麦克风权限检查 ===")
    logger.warning("此应用需要麦克风权限才能进行录音。")
    logger.warning("\n请按照以下步骤授予权限：")
    logger.warning("1. 打开 系统偏好设置")
    logger.warning("2. 点击 隐私与安全性")
    logger.warning("3. 点击左侧的 麦克风")
    logger.warning("4. 点击右下角的锁图标并输入密码")
    logger.warning("5. 在右侧列表中找到 Terminal（或者您使用的终端应用）并勾选")
    logger.warning("\n授权后，请重新运行此程序。")
    logger.warning("===============================\n")

class VoiceAssistant:
    def __init__(self):
        self.audio_recorder = AudioRecorder()
        self.whisper_processor = WhisperProcessor()
        self.keyboard_manager = KeyboardManager(
            on_record_start=self.start_transcription_recording,
            on_record_stop=self.stop_transcription_recording,
            on_translate_start=self.start_translation_recording,
            on_translate_stop=self.stop_translation_recording
        )
    
    def start_transcription_recording(self):
        """开始录音（转录模式）"""
        self.audio_recorder.start_recording()
    
    def stop_transcription_recording(self):
        """停止录音并处理（转录模式）"""
        audio_path = self.audio_recorder.stop_recording()
        if audio_path:
            result = self.whisper_processor.process_audio(
                audio_path,
                mode="transcriptions",
                prompt=""
            )
            # 解构返回值
            text, error = result if isinstance(result, tuple) else (result, None)
            self.keyboard_manager.type_text(text, error)
    
    def start_translation_recording(self):
        """开始录音（翻译模式）"""
        self.audio_recorder.start_recording()
    
    def stop_translation_recording(self):
        """停止录音并处理（翻译模式）"""
        audio_path = self.audio_recorder.stop_recording()
        if audio_path:
            text = self.whisper_processor.process_audio(
                audio_path,
                mode="translations",
                prompt=""
            )
            if text:
                self.keyboard_manager.type_text(text)
    
    def run(self):
        """运行语音助手"""
        logger.info("=== 语音助手已启动 ===")
        logger.info("按住 Option 键：实时语音转录（保持原文）")
        logger.info("快速双击并按住 Option 键：实时语音翻译（翻译成英文）")
        self.keyboard_manager.start_listening()

def main():
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        error_msg = str(e)
        if "Input event monitoring will not be possible" in error_msg:
            check_accessibility_permissions()
            sys.exit(1)
        elif "无法访问音频设备" in error_msg:
            check_microphone_permissions()
            sys.exit(1)
        else:
            logger.error(f"发生错误: {error_msg}", exc_info=True)
            sys.exit(1)

if __name__ == "__main__":
    main() 