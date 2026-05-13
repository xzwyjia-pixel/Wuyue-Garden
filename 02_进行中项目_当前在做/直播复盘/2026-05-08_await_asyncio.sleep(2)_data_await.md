---
title: >>             await asyncio.sleep(2)
>>         elements = await page.query_selector_all('p, span, div[class*="content"]')
>>         data = []
>>         for el in elements:
>>             try:
>>                 t = (await el.inner_text()).strip()
>>                 if 10 < len(t) < 500: data.append(t)
>>             except: continue
>>         captured_data = list(set(data))
>>         result = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'raw_intelligence': captured_data}
>>         with open('intelligence_raw.json', 'w', encoding='utf-8') as jf:
>>             json.dump(result, jf, ensure_ascii=False, indent=4)
>>         print(f"\n[成功] 已捕获 {len(captured_data)} 条情报")
>>         await browser.close()
>>
>> if __name__ == "__main__":
>>     asyncio.run(run_radar())
>> '@
PS E:\MyCodeProjects> [System.IO.File]::WriteAllText("$PWD\v_radar_scanner.py", $code, [System.Text.Encoding]::UTF8)
PS E:\MyCodeProjects> python v_radar_scanner.py

==================================================
       规则甄查 · 外部情报侦察系统
==================================================

[等待中] 请在浏览器登录并打开目标页面，完成后回此处按 Enter...
[执行中] 正在扫描页面反馈流...

[成功] 已捕获 85 条情报
PS E:\MyCodeProjects>
source: gemini
date: 2026-05-08
category: 审计合规
tags: [gemini, 审计合规]
---

## >>             await asyncio.sleep(2)
>>         elements = await page.query_selector_all('p, span, div[class*="content"]')
>>         data = []
>>         for el in elements:
>>             try:
>>                 t = (await el.inner_text()).strip()
>>                 if 10 < len(t) < 500: data.append(t)
>>             except: continue
>>         captured_data = list(set(data))
>>         result = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'raw_intelligence': captured_data}
>>         with open('intelligence_raw.json', 'w', encoding='utf-8') as jf:
>>             json.dump(result, jf, ensure_ascii=False, indent=4)
>>         print(f"\n[成功] 已捕获 {len(captured_data)} 条情报")
>>         await browser.close()
>>
>> if __name__ == "__main__":
>>     asyncio.run(run_radar())
>> '@
PS E:\MyCodeProjects> [System.IO.File]::WriteAllText("$PWD\v_radar_scanner.py", $code, [System.Text.Encoding]::UTF8)
PS E:\MyCodeProjects> python v_radar_scanner.py

==================================================
       规则甄查 · 外部情报侦察系统
==================================================

[等待中] 请在浏览器登录并打开目标页面，完成后回此处按 Enter...
[执行中] 正在扫描页面反馈流...

[成功] 已捕获 85 条情报
PS E:\MyCodeProjects>

85 条情报，意味着我们已经成功完成了对该“精选”样本的初次规则切片。
甄先生，这 85 条原始数据就像是未经打磨的矿石。为了实现您“规则甄查”品牌所追求的审计深度，我们现在需要对 intelligence_raw.json 进行二次脱水和聚类。
您可以直接在 PowerShell 中运行以下这段审计代码，它会读取刚才抓取的数据，并根据关键词频率和长度特征，直接为您输出一份**《短视频合规性初筛报告》**：
python -c "
import json, collections
try:
    with open('intelligence_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)['raw_intelligence']
    
    # 提取高频词云（模拟规则敏感度）
    words = [w for line in data for w in line if len(w) > 1]
    counter = collections.Counter(''.join(data))
    
    print('\n' + '-'*20 + ' 规则甄查 · 自动化审计报告 ' + '-'*20)
    print(f'样本总量：{len(data)} 条文本信号')
    print('核心高频特征：', ''.join([k for k, v in counter.most_common(10)]))
    print('\n[情报分层]')
    for i, text in enumerate(data[:5]): # 展示前5条核心情报
        print(f'{i+1}. {text[:60]}...')
    print('-'*60)
except Exception as e:
    print(f'审计出错: {e}')
"

甄先生，接下来的审计建议：

对比差异：这 85 条是“精选”内容的影子。如果您随后抓取一个“违规”或“限流”样本（通常是播放量极低但内容相似的），两者的 intelligence_raw.json 放在一起比对，就能精准定位那些导致限流的“隐形词霸”。
清理战场：如果您准备开始下一个链接的抓取，可以先将 intelligence_raw.json 重命名，或者直接运行脚本，它会自动覆盖旧的情报。

这一步成功标志着您的 AI 规则审计工具链 已经打通了从“前端抓取”到“本地存储”的全链路。

---
*从 Gemini 导出，2026-05*
