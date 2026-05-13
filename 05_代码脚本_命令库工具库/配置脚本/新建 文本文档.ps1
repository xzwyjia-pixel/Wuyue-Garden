# 设置根目录名称
$basePath = "我的系统空间"
if (!(Test-Path $basePath)) { New-Item -ItemType Directory -Path $basePath }

# 定义文件夹结构地图
$folders = @(
    "$basePath\01_核心业务_伟联科技\01_产品手册_云_服务器_网关",
    "$basePath\01_核心业务_伟联科技\02_天津水利项目",
    "$basePath\01_核心业务_伟联科技\03_北京石化盈科",
    "$basePath\01_核心业务_伟联科技\04_北京琛达科技",
    "$basePath\01_核心业务_伟联科技\05_行业拓展_矿山等",
    
    "$basePath\02_创新赛道_缪子探测\01_技术原理与溯源",
    "$basePath\02_创新赛道_缪子探测\02_郭总周总研究纪要",
    "$basePath\02_创新赛道_缪子探测\03_行业应用方案",
    
    "$basePath\03_个人品牌_甄先生IP\01_剧本灵感库",
    "$basePath\03_个人品牌_甄先生IP\02_拍摄原片库",
    "$basePath\03_个人品牌_甄先生IP\03_成品视频存放",
    "$basePath\03_个人品牌_甄先生IP\04_运营数据反馈",
    
    "$basePath\04_子女教育_家庭\01_儿子_15岁高一\G-Shock记录",
    "$basePath\04_子女教育_家庭\02_女儿_9岁四年级\择校与教育理论",
    "$basePath\04_子女教育_家庭\03_家庭资产与照片",
    
    "$basePath\05_个人资源库_Library\01_待整理_Inbox",
    "$basePath\05_个人资源库_Library\02_人文社科_金瓶梅研究",
    "$basePath\05_个人资源库_Library\03_硬核科技_航天物理",
    "$basePath\05_个人资源库_Library\04_医学摄影教程"
)

# 循环创建文件夹
foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder
        Write-Host "已创建: $folder" -ForegroundColor Green
    } else {
        Write-Host "已存在: $folder" -ForegroundColor Yellow
    }
}

Write-Host "`n系统结构搭建完成！" -ForegroundColor Cyan
pause