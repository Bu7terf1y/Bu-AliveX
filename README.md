# Bu-AliveX

批量检测网站存活状态的工具

## 功能特性

- 手动输入URL检测
- 从文件批量读取URL
- 多线程并发检测
- 自动识别网页编码（UTF-8、GBK等）
- 结果保存为CSV文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

运行程序：

```bash
python Bu-AliveX.py
```

选择功能：
1. 手动输入 - 输入URL，空行结束
2. 读取文件 - 从 `targets.txt` 读取URL
3. 设置线程 - 设置并发线程数
4. 退出 - 退出程序

## targets.txt 格式

每行一个URL或域名：

```
baidu.com
gpnu.edu.cn
https://github.com
```

## 结果保存

结果保存在 `result/` 目录，文件名格式为 `YYYY-MM-DD_HH-MM-SS.csv`

## 项目地址

https://github.com/Bu7terf1y/Bu-AliveX

## By

Bu7terf1y
