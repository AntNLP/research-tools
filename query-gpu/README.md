# Tool: Query GPU Server

查询多台服务器的显卡使用情况，帮助快速选择可用的GPU，工具特性
+ 按照显卡空闲内存从大到小排序
+ 热力图显示显卡繁忙程度，绿色代表空闲，红色代表繁忙 
+ 可选参数 `-u` 显示每张显卡的用户（支持多个）


示例1，默认显示：

```shell
query_gpu host1 host2 ...
```
![example-image](example_mac.jpg)

示例2，额外显示用户信息：

```shell
query_gpu -u host1 host2 ...
```
![example-image](example_linux.jpeg)


列名    | 含义
:-------| :--- 
IP      | 服务器IP别名
Card    | GPU ID ([0], [1] ...) + 显卡名称
FreeMem | 空闲显存 MB (降序排序关键字)
GPU%    | GPU 当前算力占用百分比
Mem%    | GPU 当前显存占用百分比
Users   | (`-u` 可选) 用户名


## 安装方式

### Step0: 克隆本仓库并进入当前工具文件夹

```shell
git clone https://github.com/AntNLP/research-tools.git
cd research-tools/query-gpu
```

### Step1: 检查 `python` 版本并安装辅助工具包

```shell
python --version  # >= 3.6.12
pip install rich>=11.2.0
```

### Step2: 设置 ssh 服务器免密登录并设置别名

免密登录设置参考：👉🏻 https://www.cnblogs.com/jhao/p/12917598.html

设置别名，例如设置 `66` 为 `abc@123.123.123.66` 的别名，设置 `88` 为 `xyz@123.123.123.88` 的别名：

```shell
vim ~/.ssh/config

~/.ssh/config
Host 66
     HostName 123.123.123.66
     User abc
     Port 22

Host 88
     HostName 123.123.123.88
     User xyz
     Port 22
```


### Step3: 复制命令并执行

对于 Linux/Mac OS 用户（有 ROOT 权限），
```shell
sudo cp query_gpu.py /usr/local/bin/query_gpu
sudo chmod 755 /usr/local/bin/query_gpu
query_gpu 66 88
```

对于 Linux/Mac OS 用户（没有 ROOT 权限），
```shell
cp query_gpu.py ~/.local/bin/query_gpu
export PATH=~/.local/bin/:$PATH
chmod 755 ~/.local/bin/query_gpu
query_gpu 66 88
```