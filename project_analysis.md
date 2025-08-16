# Whisper Input 项目分析报告

## 1. 项目概述

Whisper Input 是一个基于 Python 的语音输入工具，受到即友 FeiTTT 的启发而开发。该项目可以实现通过按下 Option 按钮开始录制语音，抬起按钮结束录制，并调用 Groq 的 Whisper Large V3 Turbo 模型或 SiliconFlow 托管的 FunAudioLLM/SenseVoiceSmall 模型进行语音转录。

由于 Groq 和 SiliconFlow 都提供免费用量，用户无需付费即可使用该工具。SiliconFlow 托管的 SenseVoiceSmall 模型具有速度更快、识别更准确、自带标点符号且无用量限制的优势。

## 2. 核心功能

### 2.1 语音转录
- 支持多语言语音转录
- 快捷键：Option 或 Alt

### 2.2 语音翻译
- 支持中文翻译为英文
- 快捷键：Shift + Option 或 Shift + Alt

### 2.3 多平台支持
- macOS 支持（主要平台）
- Windows 支持（实验性）

### 2.4 高级功能
- 繁体中文转简体中文
- 自动添加标点符号
- 识别结果优化（实验性）
- 剪贴板内容管理

## 3. 技术架构

### 3.1 整体架构
```
Whisper Input/
├── main.py                 # 主程序入口
├── control_ui.py           # 图形界面控制程序
├── .env.example            # 配置文件模板
├── requirements.in         # 依赖定义文件
├── requirements.txt        # 锁定版本的依赖文件
├── src/                    # 核心源代码
│   ├── audio/              # 音频处理模块
│   ├── keyboard/           # 键盘监听模块
│   ├── llm/                # 大语言模型处理模块
│   ├── transcription/      # 语音转录模块
│   └── utils/              # 工具模块
└── logs/                   # 日志目录
```

### 3.2 核心组件
1. **音频录制模块** (`src/audio/recorder.py`)：负责音频录制和处理
2. **键盘监听模块** (`src/keyboard/listener.py`)：监听快捷键事件
3. **语音转录模块** (`src/transcription/whisper.py`, `src/transcription/senseVoiceSmall.py`)：调用不同平台的语音转录API
4. **LLM处理模块** (`src/llm/`)：处理文本优化、标点符号添加和翻译
5. **UI控制模块** (`control_ui.py`)：提供图形界面控制程序运行

## 4. 主要模块分析

### 4.1 主程序 (`main.py`)
- 程序入口点，初始化各个组件
- 根据配置选择使用 Groq 或 SiliconFlow 平台
- 管理整个语音助手的运行流程

### 4.2 音频录制模块 (`src/audio/recorder.py`)
- 使用 `sounddevice` 库进行音频录制
- 支持实时音频流录制，无需保存到本地文件
- 自动检测和适应不同的音频设备
- 设置最小录音时长（1秒）以避免误触发

### 4.3 键盘监听模块 (`src/keyboard/listener.py`)
- 使用 `pynput` 库监听键盘事件
- 支持 Option/Alt 键和 Shift 键组合操作
- 实现状态管理（空闲、录音、翻译、处理等）
- 处理临时文本显示和剪贴板操作

### 4.4 语音转录模块
#### 4.4.1 Whisper 处理器 (`src/transcription/whisper.py`)
- 调用 Groq 平台的 Whisper API
- 支持转录和翻译两种模式
- 集成繁体转简体、标点符号添加和结果优化功能

#### 4.4.2 SenseVoiceSmall 处理器 (`src/transcription/senseVoiceSmall.py`)
- 调用 SiliconFlow 平台的 SenseVoiceSmall API
- 内置标点符号，无需额外处理
- 集成翻译功能

### 4.5 LLM 处理模块
#### 4.5.1 符号处理器 (`src/llm/symbol.py`)
- 使用大语言模型为文本添加标点符号
- 优化识别结果（实验性功能）

#### 4.5.2 翻译处理器 (`src/llm/translate.py`)
- 使用 SiliconFlow 平台的大语言模型进行中英翻译

### 4.6 UI 控制模块 (`control_ui.py`)
- 基于 PyQt5 的图形界面
- 提供 API Key 设置和管理
- 实时显示程序运行日志
- 控制程序启动和停止

### 4.7 工具模块
#### 4.7.1 日志模块 (`src/utils/logger.py`)
- 使用 `colorlog` 实现彩色日志输出
- 同时输出到控制台和文件
- 支持日志轮转

#### 4.7.2 状态管理 (`src/keyboard/inputState.py`)
- 使用枚举类型管理程序状态
- 提供状态转换的逻辑判断

## 5. 依赖关系

### 5.1 核心依赖
- `pynput`: 键盘监听
- `sounddevice` & `soundfile`: 音频录制和处理
- `openai`: 调用 Groq API
- `httpx` & `requests`: HTTP 请求处理
- `PyQt5`: 图形界面
- `python-dotenv`: 环境变量管理
- `pyperclip`: 剪贴板操作
- `numpy`: 数值计算

### 5.2 工具依赖
- `pip-tools`: 依赖管理
- `colorlog`: 彩色日志输出
- `opencc-python-reimplemented`: 繁简转换

## 6. 配置说明

项目通过 `.env` 文件进行配置，主要配置项包括：

### 6.1 平台配置
- `SERVICE_PLATFORM`: 选择服务提供商（siliconflow / groq）
- `SYSTEM_PLATFORM`: 系统平台（mac / win）

### 6.2 API 密钥
- `SILICONFLOW_API_KEY`: SiliconFlow API 密钥
- `GROQ_API_KEY`: Groq API 密钥

### 6.3 快捷键配置
- `TRANSCRIPTIONS_BUTTON`: 转录按钮（默认 alt）
- `TRANSLATIONS_BUTTON`: 翻译按钮（默认 shift）

### 6.4 功能配置
- `CONVERT_TO_SIMPLIFIED`: 是否转换繁体中文为简体
- `ADD_SYMBOL`: 是否添加标点符号
- `OPTIMIZE_RESULT`: 是否优化识别结果
- `KEEP_ORIGINAL_CLIPBOARD`: 是否保留原始剪贴板内容

## 7. 使用方法

### 7.1 环境准备
1. 确保本地有 Python 环境（版本不低于 3.10）
2. 推荐使用 Python 3.12.5（避免 3.13.1 的光标切换问题）

### 7.2 安装步骤
```bash
# 克隆项目
git clone git@github.com:ErlichLiu/Whisper-Input.git

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 安装依赖
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

### 7.3 配置 API 密钥
1. 复制 `.env.example` 为 `.env`
2. 根据选择的平台（Groq 或 SiliconFlow）填写相应的 API 密钥

### 7.4 运行程序
```bash
python main.py
```

或者使用图形界面：
```bash
python control_ui.py
```

## 8. 项目优势与局限性

### 8.1 优势
1. **多平台支持**：同时支持 macOS 和 Windows 系统
2. **双 API 支持**：可选择 Groq 或 SiliconFlow 平台
3. **快速响应**：得益于 Groq 和 SiliconFlow 的高性能，大部分语音输入可在 1-2 秒内反馈
4. **免费使用**：两个平台都提供充足的免费用量
5. **高准确性**：Whisper 和 SenseVoiceSmall 模型都具有强大的语音识别能力
6. **易用性**：简单的快捷键操作，无需复杂设置
7. **扩展功能**：支持繁简转换、标点符号添加、结果优化等高级功能

### 8.2 局限性
1. **权限要求**：需要麦克风和辅助功能权限
2. **后台运行**：程序需要一直在后台运行
3. **实验性功能**：部分功能（如结果优化）标记为实验性
4. **系统依赖**：需要特定版本的 Python 环境

## 9. 未来发展方向

根据 README 中的计划，项目未来可能的发展方向包括：
1. 添加 Agents 功能，实现更智能的交互
2. 继续完善 macOS 客户端和无障碍支持
3. 可能开发 Windows 客户端

## 10. 总结

Whisper Input 是一个功能完善、易于使用的语音输入工具。它充分利用了现代语音识别技术的优势，为用户提供快速、准确的语音转文字服务。通过支持多种平台和 API 提供商，项目具有良好的灵活性和可扩展性。对于需要频繁进行语音输入的用户，特别是视力障碍用户，这个工具提供了极大的便利性。
