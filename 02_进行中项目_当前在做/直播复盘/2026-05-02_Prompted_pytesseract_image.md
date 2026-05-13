---
title: Prompted
source: gemini
date: 2026-05-02
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

太棒了！从截图 image_c28700.png 可以看到，所有的核心工具库都已经成功导入并验证通过。你现在已经拥有了一套完整的“规则甄查”基础环境。
接下来，为了让你这套工具真正“跑”起来，我们需要处理最后一个关键环节：OCR（文字识别）引擎的本地配置。
⚠️ 必须注意的一个“坑”
虽然你已经在 Python 里安装了 pytesseract，但它只是一个“调用器”。要识别图片里的文字，你的电脑系统里必须安装 Tesseract-OCR 引擎 本体。
如果你现在运行 pytesseract.image_to_string()，大概率会报错：TesseractNotFoundError。

第一步：安装 Tesseract-OCR 引擎

下载： 访问 Tesseract at UB Mannheim 下载最新版的 Windows 64位安装包（.exe）。
安装时勾选中文： 在安装过程中，有一个 "Additional script data" 和 "Additional language data" 选项，请务必勾选 "Chinese (Simplified)"，否则它识别不出中文。
记住路径： 默认路径通常是 C:\Program Files\Tesseract-OCR。


第二步：在代码中关联引擎
安装好后，你在编写甄查脚本时，需要在开头加上一句话，告诉程序引擎在哪里：
import pytesseract

# 这一行非常重要，指向你安装 exe 的具体位置
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


第三步：实战演练——写一个“封面文字提取”小脚本
既然你的环境已经准备好了，你可以试着创建一个 .py 文件，跑一下这段代码。它能帮你自动提取图片中的文字，这也是 “规则甄查 - 甄先生” 项目的核心功能之一：
import PIL.Image as Image
import pytesseract

# 1. 设置引擎路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def check_image_text(image_path):
    try:
        # 2. 打开图片
        img = Image.open(image_path)
        # 3. 识别中文和英文
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        
        print("--- 提取到的封面文字 ---")
        print(text)
        
        # 4. 简单的风险核查示例
        danger_words = ['最', '第一', '绝对', '赚钱'] # 举例一些违规词
        for word in danger_words:
            if word in text:
                print(f"⚠️ 风险预警：检测到疑似违规词【{word}】")
                
    except Exception as e:
        print(f"识别出错：{e}")

# 使用时只需换成你本地图片的路径
# check_image_text('cover.jpg')


甄先生，下一步建议：
你目前已经具备了开发 “规则甄查” 工具的技术闭环。鉴于你丰富的项目背景和对短视频算法规则的持续研究：

规则库建设： 你可以利用已安装的 requests 和 beautifulsoup4 抓取抖音官方的《创作规范》，建立一个本地的“违规词库”。
自动化流程： 将这个脚本与你的视频分析逻辑结合，实现上传视频即刻输出合规性报告。

需要我帮你写一段专门用来抓取网页上“违规词表”的代码吗？ 这样你就可以直接拿来和封面识别的结果做对比了。

---
*从 Gemini 导出，2026-05*
