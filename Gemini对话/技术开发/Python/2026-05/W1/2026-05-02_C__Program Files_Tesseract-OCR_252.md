---
title: C:\Program Files\Tesseract-OCR这个路径打不开
source: gemini
date: 2026-05-02
category: 技术开发
subcategory: Python
old_category: 编程开发
tags: [gemini, 技术开发, Python]
---

## C:\Program Files\Tesseract-OCR这个路径打不开

## C:\Program Files\Tesseract-OCR这个路径打不开

---

### 第四步：检查中文包（重要！）
既然你的项目是 **“规则甄查”**，肯定需要识别中文。
1.  进入你找回的那个 Tesseract 文件夹。
2.  进入 `tessdata` 子文件夹。
3.  看看里面有没有一个叫 `chi_sim.traineddata` 的文件？
    *   **如果没有：** 你需要重新运行安装包，在安装时的组件选择界面，勾选 `Additional language data` -> `Chinese (Simplified)`。

### 总结：
**报错 `TesseractNotFoundError` 唯一的原因就是：代码里写的路径下，找不到那个 .exe 文件。**

只要你安装好软件，并把 `config.py` 里的路径改成实际存在的那个路径，`python main.py` 就能瞬间跑通！

**甄先生，您现在重新安装一下软件试试？** 如果安装过程中有任何弹窗这就找到了问题的根源！如果路径打不开，说明 **Tesseract-OCR 软件本体还没有成功安装到这个位置**，或者安装时的路径不是默认路径。

这就好比你写好了拨号程序（代码），但电话机（软件）还没装好，所以怎么拨号都会提示“找不到设备”。

请按照以下详细步骤重新操作：

### 第一步：确认软件是否已下载并安装
1.  **去哪里下载？**
    请直接点击这个链接下载安装包：[tesseract-ocr-w64-setup-5.3.3.exe](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe)
2.  **安装时注意：**
    运行安装包时，请一路点击 `Next`。当看到选择安装目录时，**记下那个路径**（默认确实应该是 `C:\Program Files\Tesseract-OCR`）。

---

### 第二步：如果你已经安装过，找回真实的路径
如果你觉得已经装过了，但不确定在哪，可以这样找：
1.  点击 Windows 的 **“开始”菜单**，搜索 `Tesseract`。
2.  在搜索结果上点**右键** -> **“打开文件位置”**。
3.  如果打开的是快捷方式，再对那个快捷方式点**右键** -> **“打开文件所在的位置”**。
4.  **这就是真实的路径！** 请复制上方地址栏里的路径。

---

### 第三步：根据真实路径修改 `config.py`
假设你发现真实的安装路径是 `D:\Software\Tesseract-OCR`，那么请把你的 `config.py` 改成：
```python
# 将引号内的内容替换为您刚刚找到的真实路径，末尾必须带上 \tesseract.exe
TESSERACT_EXE_PATH = r'D:\Software\Tesseract-OCR\tesseract.exe'


第四步：检查中文包（重要！）
既然你的项目是 “规则甄查”，肯定需要识别中文。

进入你找回的那个 Tesseract 文件夹。
进入 tessdata 子文件夹。
看看里面有没有一个叫 chi_sim.traineddata 的文件？

如果没有： 你需要重新运行安装包，在安装时的组件选择界面，勾选 Additional language data -> Chinese (Simplified)。



总结：
报错 TesseractNotFoundError 唯一的原因就是：代码里写的路径下，找不到那个 .exe 文件。
只要你安装好软件，并把 config.py 里的路径改成实际存在的那个路径，python main.py 就能瞬间跑通！
甄先生，您现在重新安装一下软件试试？ 如果安装过程中有任何弹窗提示不确定的，可以截图发给我。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 技术开发 / Python · 2026-05-02*
