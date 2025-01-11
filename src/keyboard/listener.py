from pynput.keyboard import Controller, Key, Listener
import pyperclip
from ..utils.logger import logger
import time
from enum import Enum, auto

class InputState(Enum):
    """输入状态枚举"""
    IDLE = auto()           # 空闲状态
    RECORDING = auto()      # 正在录音
    RECORDING_TRANSLATE = auto()  # 正在录音(翻译模式)
    PROCESSING = auto()     # 正在处理
    TRANSLATING = auto()    # 正在翻译
    ERROR = auto()          # 错误状态
    WARNING = auto()        # 警告状态（用于录音时长不足等提示）

    @property
    def is_recording(self):
        """检查是否处于录音状态"""
        return self in (InputState.RECORDING, InputState.RECORDING_TRANSLATE)
    
    @property
    def can_start_recording(self):
        """检查是否可以开始新的录音"""
        return not self.is_recording

class KeyboardManager:
    def __init__(self, on_record_start, on_record_stop, on_translate_start, on_translate_stop):
        self.keyboard = Controller()
        self.option_pressed = False
        self.shift_pressed = False
        self.temp_text_length = 0  # 用于跟踪临时文本的长度
        self.processing_text = None  # 用于跟踪正在处理的文本
        self.error_message = None  # 用于跟踪错误信息
        self.warning_message = None  # 用于跟踪警告信息
        
        # 回调函数
        self.on_record_start = on_record_start
        self.on_record_stop = on_record_stop
        self.on_translate_start = on_translate_start
        self.on_translate_stop = on_translate_stop
        
        # 状态管理
        self._state = InputState.IDLE
        self._state_messages = {
            InputState.IDLE: "",
            InputState.RECORDING: "🎤 正在录音...",
            InputState.RECORDING_TRANSLATE: "🎤 正在录音 (翻译模式)",
            InputState.PROCESSING: "🔄 正在转录...",
            InputState.TRANSLATING: "🔄 正在翻译...",
            InputState.ERROR: lambda msg: f"{msg}",  # 错误消息使用函数动态生成
            InputState.WARNING: lambda msg: f"⚠️ {msg}"  # 警告消息使用函数动态生成
        }
    
    @property
    def state(self):
        """获取当前状态"""
        return self._state
    
    @state.setter
    def state(self, new_state):
        """设置新状态并更新UI"""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            
            # 获取状态消息
            message = self._state_messages[new_state]
            if callable(message):  # 如果是函数（用于错误/警告消息）
                if new_state == InputState.ERROR:
                    message = message(self.error_message)
                else:  # WARNING
                    message = message(self.warning_message)
            
            # 删除之前的提示文字
            self._delete_previous_text()
            
            # 根据状态转换类型显示不同消息
            if new_state in (InputState.PROCESSING, InputState.TRANSLATING):
                # 处理或翻译状态
                self.processing_text = message
                self.type_temp_text(message)
            elif new_state in (InputState.ERROR, InputState.WARNING):
                # 错误或警告状态
                self.type_temp_text(message)
                self.schedule_message_clear(new_state)
            elif new_state in (InputState.RECORDING, InputState.RECORDING_TRANSLATE):
                # 录音状态
                self.type_temp_text(message)
            elif new_state == InputState.IDLE:
                # 空闲状态，清除所有临时文本
                self.processing_text = None
            else:
                # 其他状态
                self.type_temp_text(message)
    
    def schedule_message_clear(self, message_state):
        """计划清除消息"""
        def clear_message():
            time.sleep(2)  # 警告消息显示2秒
            if self.state == message_state:
                if message_state == InputState.ERROR:
                    self.error_message = None
                else:  # WARNING
                    self.warning_message = None
                self.state = InputState.IDLE
        
        import threading
        threading.Thread(target=clear_message, daemon=True).start()
    
    def show_warning(self, warning_message):
        """显示警告消息"""
        self.warning_message = warning_message
        self.state = InputState.WARNING
    
    def show_error(self, error_message):
        """显示错误消息"""
        self.error_message = error_message
        self.state = InputState.ERROR
    
    def type_text(self, text, error_message=None):
        """将文字输入到当前光标位置
        
        Args:
            text: 要输入的文本或包含文本和错误信息的元组
            error_message: 错误信息
        """
        # 如果text是元组，说明是从process_audio返回的结果
        if isinstance(text, tuple):
            text, error_message = text
            
        if error_message:
            self.show_error(error_message)
            return
            
        if not text:
            # 如果没有文本且不是错误，可能是录音时长不足
            if self.state in (InputState.PROCESSING, InputState.TRANSLATING):
                self.show_warning("录音时长过短，请至少录制1秒")
            return
            
        try:
            logger.info("正在输入转录文本...")
            self._delete_previous_text()
            # 先输入文本和完成标记
            pyperclip.copy(text + " ✅")
            with self.keyboard.pressed(Key.cmd):
                self.keyboard.press('v')
                self.keyboard.release('v')
            
            # 等待一小段时间确保文本已输入
            time.sleep(0.5)
            
            # 删除完成标记（2个字符：空格和✅）
            for _ in range(2):
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)
            
            logger.info("文本输入完成")
            
            # 清理处理状态
            self.processing_text = None
            self.state = InputState.IDLE
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
            self.show_error(f"❌ 文本输入失败: {e}")
    
    def _delete_previous_text(self):
        """删除之前输入的临时文本"""
        if self.temp_text_length > 0:
            for _ in range(self.temp_text_length):
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)
            self.temp_text_length = 0
    
    def type_temp_text(self, text):
        """输入临时状态文本"""
        if not text:
            return
        self._delete_previous_text()
        pyperclip.copy(text)
        with self.keyboard.pressed(Key.cmd):
            self.keyboard.press('v')
            self.keyboard.release('v')
        self.temp_text_length = len(text)
    
    def on_press(self, key):
        """按键按下时的回调"""
        try:
            if key == Key.alt_l:  # Option 键按下
                self.option_pressed = True
                if self.shift_pressed and self.state.can_start_recording:
                    self.state = InputState.RECORDING_TRANSLATE
                    self.on_translate_start()
                elif self.state.can_start_recording:
                    self.state = InputState.RECORDING
                    self.on_record_start()
            elif key == Key.shift:  # Shift 键按下
                self.shift_pressed = True
                if self.option_pressed and self.state.can_start_recording:
                    self.state = InputState.RECORDING_TRANSLATE
                    self.on_translate_start()
        except AttributeError:
            pass

    def on_release(self, key):
        """按键释放时的回调"""
        try:
            if key == Key.alt_l:  # Option 键释放
                self.option_pressed = False
                if self.state == InputState.RECORDING_TRANSLATE:
                    # 先设置状态为翻译中
                    self.state = InputState.TRANSLATING
                    # 然后停止录音并处理
                    audio_path = self.on_translate_stop()
                    if audio_path is None:
                        self._delete_previous_text()
                        self.state = InputState.IDLE
                elif self.state == InputState.RECORDING:
                    # 先设置状态为处理中
                    self.state = InputState.PROCESSING
                    # 然后停止录音并处理
                    audio_path = self.on_record_stop()
                    if audio_path is None:
                        self._delete_previous_text()
                        self.state = InputState.IDLE
            elif key == Key.shift:  # Shift 键释放
                self.shift_pressed = False
                if self.state == InputState.RECORDING_TRANSLATE and not self.option_pressed:
                    # 先设置状态为翻译中
                    self.state = InputState.TRANSLATING
                    # 然后停止录音并处理
                    audio_path = self.on_translate_stop()
                    if audio_path is None:
                        self._delete_previous_text()
                        self.state = InputState.IDLE
        except AttributeError:
            pass
    
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