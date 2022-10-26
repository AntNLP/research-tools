# research-tools

本项目库是 `AntNLP` 团队在科研生活中常用的实用工具。

## 1. 👉🏻 [gpu-server-usage](./gpu-server-usage)

描述服务器的基本配置，包括
+ 文件系统管理
+ Zsh Shell
+ 虚拟环境工具Anaconda
+ 预训练模型库 Transformers
+ 深度学习库Pytorch
+ 密钥登陆
+ 常见的FAQ

## 2. 👉🏻 [query-gpu](./query-gpu)

查询多台服务器的显卡使用情况，帮助快速选择可用的GPU，工具特性
+ 按照显卡空闲内存从大到小排序
+ 热力图显示显卡繁忙程度，绿色代表空闲，红色代表繁忙 
+ 可选参数 `-u` 显示每张显卡的用户（支持多个）