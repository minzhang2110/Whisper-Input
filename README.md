# Whisper Input

Whisper Input 是受到即友[FeiTTT](https://web.okjike.com/u/DB98BE7A-9DBB-4730-B6B9-2DC883B986B1)启发做的一个简单的 python 代码。可以实现按下 Option 按钮开始录制，抬起按钮就结束录制，并调用 Groq Whisper Large V3 Turbo 模型进行转译，由于 Groq 的速度非常快，所以大部分的语音输入都可以在 1-2s 内反馈。并且得益于 whisper 的强大能力，转译效果非常不错。

🎉🎉由于目前已经发现了更好用的语音输入软件[WhisperKeyBoard](https://whisperkeyboard.app/)，非常推荐大家可以直接使用这款软件即可。Whisper Input 的中心将继续回到 Voice + Agents 上。

## 功能

| 功能           | 快捷键                          |
| -------------- | ------------------------------- |
| 多语言语音转译 | Option 或者 Alt                 |
| 中文翻译为英文 | Shift + Option 或者 Shift + Alt |



查看[视频效果演示](https://img.erlich.fun/personal-blog/uPic/WhisperInputV02_compressed.mp4)



**重点：Groq 只要注册，就提供一定的免费用量，并且在我们这个使用场景下免费已经完全够用了！**

**🧐 目前已经支持代理模式使用 Groq Whisper 了，可以联系我为你提供对应的 API KEY。微信搜索：`geekthings`**

## 使用方法

1. 注册 Groq 账户：https://console.groq.com/login
2. 复制 Groq 免费的 API KEY：https://console.groq.com/keys
3. 打开 `终端` ，进入到想要下载项目的文件夹
    ```bash
    git clone git@github.com:ErlichLiu/Whisper-Input.git
    ```
4. 创建虚拟环境 【推荐】
    ```bash
    python -m venv venv
    ```

5. 重命名 `.env` 文件
    ```bash
    cp .env.example .env
    ```

6. 粘贴在第 2 步复制的 API KEY 到 `.env`  文件，效果类似
    ```bash
    GROQ_API_KEY=gsk_z8q3rXrQM3o******************8dQEJCYz3QTJQYZ
    ```

7. 在最好不需要关闭的 `终端` 内进入到对应文件夹，然后激活虚拟环境
    ```bash
    # macOS / Linux
    source venv/bin/activate
    
    # Windows
    .\venv\Scripts\activate
    ```

8. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```

9. 运行程序
    ```bash
    python main.py
    ```

    

**🎉  此时你就可以按下 Option 按钮开始语音识别录入啦！**



![image-20250111140954085](https://img.erlich.fun/personal-blog/uPic/image-20250111140954085.png)

## Tips

由于这个程序需要一直在后台运行，所以最好找一个自己不会经常下意识关掉的终端或者终端里的 Tab 来运行，不然很容易会不小心关掉。



关注作者个人网站，了解更多项目: https://erlich.fun





## 未来计划

[✅] 多语言转译功能

[✅] 中文或多语言转译为英文

[✅] 标点符号支持

[  ] 添加 Agents，或许可以实现一些屏幕截图，根据上下文做一些输入输出之类的



**如果你也有想法：** 欢迎 Fork 和 PR，如果你在使用当中遇到问题，欢迎提交 Issue。

## 更新日志

#### 2025.01.14
> 1. 支持语音输入结果优化，并更换推荐模型为 `Llama 3.3 70B`，同样免费

#### 2025.01.13
> 1. 支持国内网络，无需申请 Groq API KEY 可以免费使用，Erlich 提供免费代理 API KEY
> 2. 通过环境变量支持将繁体中文转化为简体中文 `.env` ，`CONVERT_TO_SIMPLIFIED=true`，默认开启
> 3. 通过环境变量支持添加标点符号功能 `.env`，`ADD_SYMBOL=true`，默认开启，可以更换模型

#### 2025.01.12
> 1. 增加了一个延迟 0.5s 的触发，方便在一些快捷键需要用到 Option/Alt 按钮时不会被误触
> 2. 重构代码

#### 2025.01.11
> 1. 支持快捷键按下后的状态显示【正在录音、正在转译/翻译、完成】
> 2. 支持多语言语音转换为英文输出

#### 2025.01.10

> 1. 支持基本的快捷键语音转文字输入

## 协议

遵循 MIT 协议