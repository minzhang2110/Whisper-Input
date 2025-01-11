from pynput.keyboard import Controller, Key, Listener
import pyperclip
from ..utils.logger import logger

class KeyboardManager:
    def __init__(self, on_record_start, on_record_stop):
        self.keyboard = Controller()
        self.option_pressed = False
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
    
    def type_text(self, text):
        """将文字输入到当前光标位置"""
        if not text:
            return
            
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
            self.on_record_start()

    def on_release(self, key):
        """按键释放时的回调"""
        if key == Key.alt_l:
            logger.debug("检测到 Option 键释放")
            self.option_pressed = False
            self.on_record_stop()
    
    def start_listening(self):
        """开始监听键盘事件"""
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

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