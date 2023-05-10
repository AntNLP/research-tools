# Tool: conda 环境同步

在多台服务器之间同步/迁移conda环境。

**前提条件：用户名相同。** conda环境里有些代码包含绝对路径，如果用户名不同，这些路径就损坏了。因此不能跨用户同步环境。

主要分为两种方法：

+ 基于 `rsync` 的同步：
  + 优点：增量更新（第一次同步是全量复制，之后的同步是增量更新）
  + 缺点：需要配置服务器之间的ssh连接（$O(n^2)$）
+ 基于文件复制的迁移：
  + 优点：操作简单。且不需要额外配置 $O(n^2)$ 的ssh连接。
  + 缺点：多一次复制。不是增量更新（每一次同步都要全量复制）。

## rsync 同步

从服务器A同步到服务器B：

#### 方法1：在服务器A上push

在服务器A上执行：

```bash
rsync -avhH --exclude __pycache__/ --delete ~/.conda $HOST_B:~
```

其中 `$HOST_B` 替换为服务器B的地址（例如 `user@ip` 或 `~/.ssh/config` 里配置的别名）

**注意：`~/.conda` 不能写成 `~/.conda/`** ([why](https://unix.stackexchange.com/a/605502))

#### 方法2：在服务器B上pull

在服务器B上执行：

```bash
rsync -avhH --exclude __pycache__/ --delete $HOST_A:~/.conda ~
```

其中 `$HOST_A` 替换为服务器A的地址（例如 `user@ip` 或 `~/.ssh/config` 里配置的别名）

## 基于文件复制的迁移

**注意：不要尝试直接scp `~/.conda` 目录，必须先tar**

从服务器A复制到服务器B：

第1步：在服务器A上执行

```bash
cd ~
tar cvf conda.tar .conda
```

第2步：将服务器A上的 `~/conda.tar` 复制到服务器B。

> 如果已经有服务器之间的ssh连接，那么直接用rsync即可。这里假设没有配置服务器之间的ssh，因此需要在本地中转一下（先从A复制到本地，再从本地复制到B）。可以用xftp等软件传送文件，也可以在命令行中用 `scp` 命令复制文件。这里以 `scp` 为例。

在本地终端执行：

```bash
scp $HOST_A:~/conda.tar .
scp ./conda.tar $HOST_B:~
```

第3步：在服务器B上执行

```bash
cd ~
tar xvf conda.tar
```

> 如果服务器B上的 `~/.conda` 已经存在且确认不需要了，可以删除：
> `rm -rf ~/.conda`

第4步：删除两台服务器上以及本地的 `conda.tar` 文件

## 原理

linux上的conda环境中存在硬链接，用以节省空间([reference](https://stackoverflow.com/questions/56266229/is-it-safe-to-manually-delete-all-files-in-pkgs-folder-in-anaconda-python))。迁移conda环境的关键就是要保留硬链接结构。`tar` `rsync -H` 都可以保留硬链接，而 `scp` 不会保留硬链接（而是重复复制文件）。
