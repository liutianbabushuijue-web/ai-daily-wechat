<div align="center">

# ☀️ AI 日报 · 每天送到微信

**AIHOT 当天日报 → GitHub Actions → Server酱 Turbo → 你的微信**

不用服务器 · 电脑无需开机 · 无大模型 API 费用 · Python 标准库

[开始配置](#-五步开始使用) · [手动检查](#-检查与首次发送) · [常见问题](#-常见问题) · [安全说明](#-公开代码私密阅读)

</div>

---

## ✨ 这个项目做什么？

每天计划在 **北京时间 08:15** 获取 AIHOT 当天日报，按原顺序摘取最多 5 条，整理为一份适合手机速读的消息，通过 Server酱 Turbo 推送到你绑定的微信渠道。

- **只看 AIHOT**：不混入商业 RSS 或英语角。
- **带上出处**：最多 5 条标题（每条最多 60 字符）、每条最多 80 字符摘要摘录，以及原始来源和 AIHOT 归属链接。
- **不冒充原创**：不另行调用大模型，不声称已独立核实报道。
- **不拿旧闻补位**：只接受北京时间当天的日报；未更新或接口异常会明确提示。
- **公开代码，私密阅读**：仓库公开，但不把日报正文发布到 README、提交、Actions 日志、Summary 或 artifacts。

> 条目按 AIHOT 原顺序选取，不是重要性排名，也不是大模型精选。摘要仅作长度截取，可能在句中结束；超长标题和摘要会显示省略号。

> 这不是逐字完整转载。部分条目可能因缺少来源链接被跳过，超过数量上限的内容请到消息中的完整日报链接阅读。

## 📱 手机阅读版

- 每条使用编号标题、短摘录、来源链接，段落之间留空行。
- 不再重复显示栏目标题，说明放在末尾，完整内容通过链接阅读。
- 微信或 Server酱页面的具体字号由接收端控制，本项目通过减少内容与改善结构降低阅读密度。
- 当前仍只用 AIHOT，没有接入模型或其他新闻源。

## 🧭 工作原理

```text
GitHub 定时唤醒（计划北京时间 08:15）
             ↓
       离线安全与解析测试
             ↓
      AIHOT 官方公开接口
             ↓
     校验日期、摘编、保留出处
             ↓
    Server酱 Turbo → 绑定的微信渠道
```

代码上传不会发消息：`push` 只运行离线测试。未配置 Secret 时，定时任务会安全跳过抓取和发送。**配置 Secret 后，后续定时任务就会自动发送**，因此请先确认自己的接收渠道。

## 🚀 五步开始使用

### 1. 准备 Server酱 Turbo

打开 [Server酱 Turbo 官网](https://sct.ftqq.com/)，用你自己的账号登录。按照网站当前引导绑定接收渠道，确认它指向你自己的微信，并检查当前额度与渠道限制。

找到并复制 Turbo 的 **SendKey**：应以 `SCT` 开头。

> 本项目只支持 Turbo 的 `SCT...`。不支持 Server酱³ 的 `sctp...` 或旧版 `SCK...`，不能靠修改前缀转换。不要在聊天、代码、Issue 或截图中提供完整 SendKey。

### 2. 在 GitHub 创建 Secret

打开本仓库：[ai-daily-wechat](https://github.com/liutianbabushuijue-web/ai-daily-wechat)。

依次点击：

**Settings → Secrets and variables → Actions → New repository secret**

| 输入项 | 填什么 |
| --- | --- |
| Name | `SERVERCHAN_SENDKEY` |
| Secret | 你刚复制的完整 Turbo SendKey |

点击 **Add secret**。注意是 **Secrets**，不是 **Variables**；不要把密钥粘进 README 或 Python 文件。

便捷入口：[本仓库 Actions Secrets 设置](https://github.com/liutianbabushuijue-web/ai-daily-wechat/settings/secrets/actions)。只有具有对应权限的账号能管理它。

### 3. 确认 Actions 可以运行

打开仓库的 **Actions** 页，找到 **Daily private briefing**。如果 GitHub 提示工作流被禁用，按页面提示启用。新建或 fork 的仓库可能需要这一步。

工作流必须存在于默认分支 `main`，定时触发才会生效。仓库设置如果禁止 Actions，也需由仓库所有者先调整。

### 4. 做一次不发送检查

按下一节的步骤手动运行，保持 `send` 为 **false**。它会测试代码、获取当天数据并检查格式，但**不会向微信发送，也不会在公开页面展示正文**。

### 5. 自己确认一次真实发送

确认接收渠道正确后，再手动运行一次，勾选 `send`（即 **true**）。这会真实推送。检查你的微信和 Server酱记录，确认成功后即可等待每天的定时任务。

> 仓库发布不代表微信已验证。本项目不会替你填写密钥，也不会在你未选择发送时发送测试消息。

## 🧪 检查与首次发送

1. 打开 [Actions](https://github.com/liutianbabushuijue-web/ai-daily-wechat/actions)。
2. 左侧选择 **Daily private briefing**。
3. 右侧点击 **Run workflow**，分支选择 `main`。
4. 首次保持 `send=false`，点击运行。
5. 打开新出现的运行记录，查看步骤状态和条目数量。**没有正文预览是安全设计，不是错误。**
6. 需要真实测试时重新运行并选择 `send=true`。

| 运行方式 | 获取 AIHOT | 发送微信 |
| --- | --- | --- |
| 上传代码触发 `push` | 否 | 否 |
| 手动 `send=false` | 是 | 否 |
| 手动 `send=true`，有 Secret | 是 | 是 |
| 每日定时，有 Secret | 是 | 是 |
| 定时或手动发送，但无 Secret | 否 | 否，显示跳过 |

**“Server酱已接受推送请求”不等于微信已经送达。** 最终要检查接收渠道和 Server酱记录。手动重复运行 `send=true` 会重复推送，没有跨运行去重。

### 想看私密预览？在自己电脑上查看（可选）

安装官方 Python 3.12 或更新版本，下载仓库并进入项目目录，执行：

```sh
python -m unittest discover -s tests -v
python briefing.py
```

然后用本机文本编辑器打开 `preview.md`。默认不发送，无需 SendKey。不要将此文件上传至 GitHub、Issue 或公开分享空间；`.gitignore` 已排除它，但不能阻止人为强制上传。

## ⏰ 修改时间、暂停和恢复

定时配置位于 [`.github/workflows/daily.yml`](.github/workflows/daily.yml)：

```yaml
- cron: '15 0 * * *'
```

GitHub cron 使用 **UTC**，北京时间为 UTC+8。例如：

| 北京时间 | UTC cron |
| --- | --- |
| 08:15 | `15 0 * * *` |
| 08:30 | `30 0 * * *` |
| 09:15 | `15 1 * * *` |

修改后保存到默认分支。过早运行可能碰到当天日报尚未出刊。

- **暂停**：Actions → Daily private briefing → 右上角菜单 → **Disable workflow**。
- **恢复**：回到工作流页面点击 **Enable workflow**。
- **替换密钥**：Settings → Secrets and variables → Actions，编辑 `SERVERCHAN_SENDKEY`。
- **停止发送但保留代码**：禁用工作流，或删除此 Secret。

## 🔒 公开代码，私密阅读

这个仓库是 **Public**：任何人都可能查看代码、提交历史和 Actions 日志。请不要把它当私人笔记本。

本项目的保护措施：

- Secret 仅注入检查/发送步骤，不出现在代码、正文、请求日志或异常堆栈中。
- 正文临时写入 runner 的临时目录，运行结束时清理；不上传 artifacts、不写 Step Summary、不打印全文。
- 日志只包含状态、数量和固定错误提示；测试数据为人工构造的示例，不包含实际日报。
- 发送仅访问固定的 Server酱 Turbo HTTPS 主机，并拒绝推送重定向。
- 工作流只有 `contents: read` 权限，检出后不保留 GitHub 凭据。
- 不安装第三方 Python 包，只使用官方 checkout/setup-python Actions。它们当前按大版本标签引用，非不可变 SHA；更严格场景可审核后固定提交。

**私密不等于端到端加密**：正文仍会由 GitHub Actions、Server酱和绑定接收渠道处理。不要加入敏感个人信息。具备仓库修改权限的人可能通过修改工作流接触 Secret，应限制协作者权限。

如果 SendKey 泄露，请先去 Server酱撤销或更换，再更新 GitHub Secret。仅删掉公开文件不等于已清除 Git 历史中的秘密。

## 🛟 常见问题

<details>
<summary><b>08:15 为什么还没收到？</b></summary>

GitHub 定时任务可能延迟，繁忙时也可能漏跑，不承诺精确到分钟。先看 Actions 是否有运行记录，再查其状态和 Server酱记录。AIHOT 是否及时出刊也影响内容；不要盲目重跑发送。

公开仓库连续约 60 天没有仓库活动时，GitHub 可能自动禁用定时工作流。检查页面是否要求重新启用，不能把首次配置当作永久可靠服务。

</details>

<details>
<summary><b>显示“尚未配置 SERVERCHAN_SENDKEY”怎么办？</b></summary>

检查名称完全匹配、Secret 建在本仓库的 Actions Secrets 下，而不是 Variables。没有 Secret 会安全跳过，不代表微信已经成功配置。

</details>

<details>
<summary><b>为什么运行是红色，但我收到了消息？</b></summary>

AIHOT 接口异常、日期过旧或内容不可解析时，开启发送的运行会发送“内容暂缺”提示，并将任务标为失败，以便提醒你检查。不会拿旧日报冒充当天日报。你可以自行在 GitHub 通知设置中配置 Actions 失败通知。

</details>

<details>
<summary><b>推送失败或超时，可以直接重跑吗？</b></summary>

先检查微信和 Server酱记录。超时可能发生在服务端已接受请求之后，因此本项目不自动重试 POST。若确认未收到且额度允许，再自行决定是否重跑。并发排队不等于去重。

</details>

<details>
<summary><b>免费吗？需要大模型 API Key 吗？</b></summary>

不需要大模型 API Key，也没有本项目额外的大模型调用费用。GitHub Actions 和 Server酱的免费额度、计费、消息长度和接收渠道限制，以各自当前规则及账户页面为准，不保证永久免费，也不会自动购买付费服务。

</details>

<details>
<summary><b>为什么 Summary 中看不到日报？</b></summary>

因为这是公开仓库。正文只用于个人接收，不作为公开预览或附件。需要查看正文，请使用本地预览或你自己的微信渠道。

</details>

## 📁 文件说明

```text
.github/workflows/daily.yml   定时、手动检查、发送与离线测试
briefing.py                  获取、校验、摘编和推送（标准库）
tests/test_briefing.py        离线测试，不调用真实推送服务
.gitignore                   排除本地预览、环境文件与缓存
README.md                    本教程
```

## 📚 来源、使用范围与可靠性

- 每次内容运行只进行一次 AIHOT GET，不自动重试，不绕过限流。
- 摘要属于 **AIHOT 内容摘录**，不是本项目独立撰写或核实的报道。
- 保留来源与归属不等于获得任意转载授权。本项目用于个人私密阅读，不应未经许可公开转载、收费、商业或批量再分发。
- 公开本项目的代码不代表可以公开日报正文，也不代表本项目授予第三方内容许可。
- 上游接口或规则变化可能需要更新解析器；请以官方最新说明为准。

官方参考：[AIHOT API](https://aihot.news/agent?tab=api) · [OpenAPI](https://aihot.news/openapi-v1.json) · [使用规则](https://aihot.news/terms) · [Server酱文档](https://sct.ftqq.com/docs/integrations/csharp/) · [GitHub 定时任务说明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

---

<div align="center">

**让代码每天醒一次，把阅读留给你。** ☕

</div>

