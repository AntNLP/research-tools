# GPU-Server Usage

## File System

我们的大容量机械硬盘挂载在`/mnt/data1`中（后续增加的硬盘会命名为`data2,data3,etc.`），需要注意的是，硬盘分为两个文件夹：`private`存放用户私有的文件；`public`存放用户之间可以共享的文件。

每个用户自己的空间位于`/mnt/data1/private/${usr_name}`，只有自己拥有完整权限，其他用户无法修改。

共享空间位于`/mnt/data1/public/${resource_name}`，组内用户可以共享语料库、外部词向量、预训练网络等，`resource_name`必须足够清晰且具有代表性。

>建议:
>
>每个用户在自己主目录下**软链接**自己的私有空间以及共享空间
>
>`ln -s /mnt/data1/private/${usr_name} /home/${usr_name}/data`
>
>`ln -s /mnt/data1/public /home/${usr_name}/public `



## ZSH-Shell

zsh是比bash更好用的shell，用户登录账号的时候会提示创建 `~/.zshrc`，此时键入数字键 `2`即可。
接着是配置 `oh-my-zsh` 网址为 https://ohmyz.sh/#install :

>安装命令👇
>
>`sh -c "$(wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"`
>插件安装参考：https://segmentfault.com/a/1190000015283092
>autojump和extract已经统一安装好，只需要安装zsh-autosuggestions和zsh-syntax-highlighting即可



## Anaconda

Anaconda为每个用户维护自己的python运行环境。目前我们在root下已经安装好了 `conda`，普通用户使用时按如下操作：

>首次使用：`conda init ${your_shell_name}` 然后==重新登录==，如果没有设置zsh就是`bash`，否则是`zsh`
>
>创建虚拟环境👇
>
>`conda create --name ${env_name} python=${py_version}`
>
>激活虚拟环境👇
>
>`conda activate ${env_name}`
>
>退出虚拟环境👇
>
>`conda deactivate`
>
>
>
>`${env_name}`建议按`py36-pt18`类似的格式建立（用以表明python版本是3.6，pytorch版本是1.8，方便确认环境是否是所需的设置）
>
>`${py_version}`是`3.6, 3.7, etc.` (推荐3.6或3.7，低于3.6的python不支持typing，高于3.7的python目前没有完整测试过pytorch)



## Transformers

Transformers作为预训练模型的统一框架在NLP领域使用频繁。

它维护了多种预训练模型，例如BERT、GPT、Roberta等。这些模型体量普遍较大（500MB+），且所有用户使用的对象都相同，所以服务器上只需保留一份模型即可。

操作方式如下：

创建新模型

1. `cd ~/public/pretrain`
2. `mkdir ${model_name}`
3. `cd ${model_name} `
4. `wget -c {config.json, tokenizer.json, pytorch_model.bin, vocab.txt and so on} ` from `https://huggingface.co/models`

使用已有模型

1. 增加环境变量 `export TRANSFORMERS_CACHE="~/public/pretrain/"`
2. 加载模型（以roberta-base为例）`tokenizer = AutoTokenizer.from_pretrained(os.environ['TRANSFORMERS_CACHE']+'roberta-base')`



## Pytorch

Pytorch稳定版1.8.2官方支持`cuda11.1`，推荐使用。

>按照如下方式安装：
>
>`conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch-lts -c nvidia`
>
>如果conda太慢，更换清华源（地址可能会变，不起作用就谷歌一下）👇
>
>`conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/`



## 密钥登陆

操作方法👇

https://www.cnblogs.com/jhao/p/12917598.html

## FAQ

1. `screen` 命令来维护多个运行界面（支持断开ssh继续运行）

2. `git-flow` 来管理代码仓库（版本控制）

3. `public` 文件夹下共享数据可以@taoji或@yfliu授权

4. `private` 文件夹下存放代码、训练参数、模型等， `public` 文件夹下存放数据、外部资源等

5. `Failed to connect to raw.githubusercontent.com port `: 

   避免DNS污染
   https://github.com/hawtim/blog/issues/10

6. `fatal: unable to access 'https://github.com/xx/xx.git/': gnutls_handshake() failed: The TLS connection was non-properly terminated.` 
   关闭SSL自签名，不需要额外的改动：

   ```
   git config --global http.sslVerify false
   ```

   
