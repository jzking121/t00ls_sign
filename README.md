**用 GitHub Actions 自动帮你每天在 T00ls 上签到拿积分**。
下面一步一步教你怎么用（无须自己买服务器，也不用自己去跑脚本）。

### 一、先 Fork 仓库

右上角点击 **Fork**，把它 Fork 到你自己的账号下。
后面的所有操作都在你自己的 Fork 仓库里完成。

---

### 二、在 Settings 里配置 Secrets（环境变量）

进入你 Fork 之后的仓库，按下面步骤：

1. 点顶部的 **Settings**
2. 左侧找到 **Secrets and variables → Actions → New repository secret**
3. 依次添加下面这些 Secrets（名字要完全一致）

必填：

* `T00LS_USERNAME`：你在 T00ls 的账号名
* `T00LS_PASSWORD`：你在 T00ls 的账号密码
* `T00LS_MD5`：

  * 如果你上面的密码是**明文密码**，这里填：`False` 或留空
  * 如果你存的是密码的 **md5 值**，这里填：`True`
* `T00LS_QID`：登录问题的 **问题 ID**（例如 1、2 之类）
* `T00LS_QANS`：登录问题的 **答案**

可选（用于微信推送结果）：

* `T00LS_SCKEY`：Server酱申请到的 `skey`，填了之后，每次签到成功/失败会给你推送通知。

---

### 三、开启 GitHub Actions

1. 在你的仓库顶部点击 **Actions**。
2. 第一次进去会看到一个提示，点 **“I understand my workflows, go ahead and enable them”** 之类的按钮，表示允许这个仓库使用 GitHub Actions

---

### 四、手动触发一次（非常关键）

GitHub 有个坑：**Fork 过来的定时任务默认不会自己跑，必须手动触发一次之后，定时才会生效。**

你可以这样做：

1. 随便改一下仓库里的文件，比如：

   * 打开 `README.md`，增加几个字，或者删几个字都行
2. 提交（Commit）这次修改。

只要有一次 `push`，GitHub Actions 里的 `T00ls Sign` workflow 就会被触发执行一次。

---

### 五、之后就会每天自动签到

仓库里已经写好了 GitHub Actions 的配置文件，会在**每天 UTC 时间 17 点（也就是北京时间凌晨 1 点左右）自动运行**签到脚本。

你也可以随时通过：

* 再 push 一次
* 或在 Actions 页面里手动点 “Run workflow”

来手动执行一次。

---

### 六、怎么看运行结果？

1. 打开仓库 → 点击 **Actions**
2. 左边流程列表里选 `T00ls Sign`
3. 点进某一次运行记录，查看日志输出。

注意仓库说明里提到：
为了做到“有一个账号失败，后面账号还能继续跑”，**这个 Action 的状态几乎总是显示绿色成功**，所以你要以日志内容为准，看里面有没有报错信息。

---


