import sounddevice as sd
import numpy as np
import queue
import soundfile as sf
import os
import tempfile
from ..utils.logger import logger

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.temp_dir = tempfile.mkdtemp()
        self._check_audio_devices()
        logger.info(f"初始化完成，临时文件目录: {self.temp_dir}")
    
    def _check_audio_devices(self):
        """检查音频设备状态"""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            logger.info(f"默认输入设备: {default_input['name']}")
            logger.info(f"支持的采样率: {default_input['default_samplerate']}")
            
            # 如果默认采样率与我们的不同，使用设备的默认采样率
            if abs(default_input['default_samplerate'] - self.sample_rate) > 100:
                self.sample_rate = int(default_input['default_samplerate'])
                logger.info(f"调整采样率为: {self.sample_rate}")
        except Exception as e:
            logger.error(f"检查音频设备时出错: {e}")
            raise RuntimeError("无法访问音频设备，请检查系统权限设置")
    
    def start_recording(self):
        """开始录音"""
        if not self.recording:
            try:
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
                    callback=audio_callback,
                    device=None,  # 使用默认设备
                    latency='low'  # 使用低延迟模式
                )
                self.stream.start()
                logger.info("音频流已启动")
            except Exception as e:
                self.recording = False
                logger.error(f"启动录音失败: {e}")
                raise
    
    def stop_recording(self):
        """停止录音并返回临时文件路径"""
        if not self.recording:
            return None
            
        logger.info("停止录音...")
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        # 收集所有音频数据
        audio_data = []
        logger.info("处理录音数据...")
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        
        if not audio_data:
            logger.warning("没有收集到音频数据")
            return None
            
        # 合并音频数据
        audio = np.concatenate(audio_data)
        logger.info(f"音频数据长度: {len(audio)} 采样点")
        
        # 保存为临时文件
        temp_path = os.path.join(self.temp_dir, "temp_audio.wav")
        sf.write(temp_path, audio, self.sample_rate)
        logger.info(f"音频已保存到临时文件: {temp_path}")
        
        return temp_path
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("临时目录已清理")
        except Exception as e:
            logger.error(f"清理临时目录失败: {e}")
    
    def __del__(self):
        self.cleanup() 