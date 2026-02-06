# 🐙 如何把项目上传到 GitHub

作为新手，把代码存到 GitHub 是个非常好的习惯！
下面是傻瓜式教程。

## 第一步：注册并创建仓库

1. 登录 [GitHub.com](https://github.com/)。
2. 点击右上角的 **+** 号，选择 **New repository** (新建仓库)。
3. **Repository name** (仓库名): 填一个名字，比如 `card-system`。
4. **Public/Private**: 
   - 选 **Private** (私有) 比较安全，因为你的代码里可能有配置信息。
   - 如果选 Public，请务必检查 `config.py` 里的密码是否改成了默认的，不要把真实密码暴露出去！
5. 点击 **Create repository**。

## 第二步：在你的电脑上操作

1. **安装 Git**:
   - 如果没安装，去 [git-scm.com](https://git-scm.com/downloads) 下载安装。
   - 安装好后，在你的项目文件夹 (`e:\暂存\Antigravity\project_one`) 空白处：
     - **右键** -> 选择 **Git Bash Here** (如果有这个选项)。
     - 或者直接打开 cmd，输入 `cd /d e:\暂存\Antigravity\project_one` 进入目录。

2. **初始化**:
   在黑框框里输入（一行一行回车）：
   ```bash
   git init
   ```
   *(这会把当前文件夹变成一个 Git 仓库)*

3. **这一步很重要！ (我已经帮你做好了)**
   确保目录下有一个 `.gitignore` 文件。这个文件会告诉 Git 不要上传垃圾文件（比如 `.db` 数据库、`__pycache__` 等）。
   *我已经帮你创建好了这个文件，所以你可以直接跳过这一步。*

4. **保存更改**:
   ```bash
   git add .
   ```
   *(注意有个点！这表示把所有文件放入暂存区)*

5. **提交代码**:
   ```bash
   git commit -m "第一次提交"
   ```

## 第三步：推送到 GitHub

1. 回到 GitHub 网页，找到 **"…or create a new repository on the command line"** 下面的几行代码。
2. 复制那行以 `git remote add origin ...` 开头的代码。
   - 比如: `git remote add origin https://github.com/你的用户名/card-system.git`
3. 在你的黑框框里粘贴并回车。
4. 这里的 `main` 是分支名，GitHub 现在默认是 main。
   ```bash
   git branch -M main
   ```
5. 最后一步，推上去！
   ```bash
   git push -u origin main
   ```
   - 可能会跳出弹窗让你登录 GitHub，登录即可。

---

## 🎉 成功！
刷新 GitHub 网页，你应该就能看到你的代码了。

## 以后怎么更新？
如果你修改了代码，想再次同步到 GitHub：

```bash
git add .
git commit -m "修改了xxx功能"
git push
```
很简单吧？
