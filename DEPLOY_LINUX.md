# 🐧 Linux 服务器部署指南

如果你想把这个系统部署到阿里云、腾讯云等 Linux 服务器上，请按照以下步骤操作。

## 1. 准备工作

确保你的服务器已经安装了 `git` (用于下载代码) 和 `python3` (用于运行代码)。

```bash
# Ubuntu / Debian 系统
sudo apt update
sudo apt install git python3 python3-pip -y

# CentOS 系统
sudo yum install git python3 python3-pip -y
```

## 2. 上传代码

你有两种方式把代码放到服务器上：

**方式 A: 直接上传文件**
使用 FTP 工具 (如 FileZilla) 或者 SFTP 把整个项目文件夹上传到服务器的 `/root/card_system` (或者其他目录)。

**方式 B: 使用 Git (如果你的代码在仓库里)**
```bash
git clone <你的仓库地址>
cd <仓库目录>
```

## 3. 运行程序

进入项目目录后，一定要先给启动脚本赋予执行权限：

```bash
cd /path/to/your/project  # 进入你存放文件的目录
chmod +x run.sh           # 赋予执行权限
```

### 方式 1: 前台运行 (测试用)
直接运行脚本，适合测试是否报错。
```bash
./run.sh
```
*注意：如果你关闭 SSH 窗口，程序会停止。*

### 方式 2: 后台运行 (推荐)
让程序在后台一直运行，即使关闭 SSH 窗口也不受影响。

```bash
nohup ./run.sh > output.log 2>&1 &
```
- `nohup`: 不挂断地运行命令。
- `> output.log`: 把日志输出到 output.log 文件，方便排查问题。
- `&`: 在后台运行。

**如何停止后台程序？**
```bash
# 1. 找到进程ID
ps -ef | grep uvicorn

# 2. 杀掉进程 (假设ID是 12345)
kill 12345
```

## 4. 开放端口

最重要的最后一步！
请务必去你的云服务器控制台 (阿里云/腾讯云的安全组设置)，**开放 TCP 8000 端口**。
否则你的浏览器是访问不了的。

- 协议: TCP
- 端口范围: 8000
- 授权对象: 0.0.0.0/0 (允许所有IP访问)

## 5. 访问

在浏览器输入：`http://<你的服务器公网IP>:8000`

---
如果有其他问题，请查看 logs 或者 output.log 文件。
