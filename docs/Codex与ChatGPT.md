# 在 Codex 和 ChatGPT Work 中使用 StudyMate

StudyMate 的 OpenAI 版本是一个技能插件：包含总控 `learning-system`、五个角色、五个规范，以及生成 HTML 课件所需的脚本、模板和数据结构。它不依赖 DSH，也不需要单独的 MCP 服务。

插件使用 OpenAI 仍支持的 `.codex-plugin/plugin.json` 兼容结构。宿主提供子代理时可委派角色，否则由同一助手按顺序执行；提问、文件操作与页面展示使用宿主已有工具。原有 `.dsh/skills/` 与 DSH 安装方式保留。

## 1. 下载完整插件

打开 [StudyMate Releases](https://github.com/Miaotofu01/Study-Mate/releases)，选择支持 Codex / ChatGPT Work 的版本，下载附件 **studymate-openai.zip**。解压后应得到包含 `.codex-plugin/`、`skills/`、`scripts/`、`templates/` 等目录的 `studymate/`。

DSH 的 npm 包与这个 ZIP 由同一条 Release 流程发布，版本一致。Codex / ChatGPT Work 用户直接使用 ZIP；课件运行环境仍需 Python 与下文列出的依赖。

### 开发者自行构建

在仓库目录运行（Node.js 版本要求见 `package.json`）：

```bash
npm run build:plugin
# 等价命令，也可以指定输出目录：
node bin/studymate.mjs build-plugin --output ./dist
```

包含此功能的 npm 版本也提供导出命令，方便开发或调试：

```bash
npx @yunmiao/studymate@latest build-plugin --output ./dist
```

`--output` 默认是当前目录下的 `dist`，相对路径以执行命令时的工作目录为准。生成：

```text
dist/
├── studymate/
│   ├── .codex-plugin/plugin.json
│   ├── skills/                  # 11 个适配后的技能
│   ├── scripts/
│   ├── templates/
│   ├── schemas/
│   └── docs/
└── studymate-openai.zip          # 完整插件分发包
```

应分发整个 `studymate` 目录或 ZIP；只复制 `skills/` 会缺少脚本和模板。构建仅生成本地文件，不会修改个人插件市场、安装到账户或发布到公共目录。

## 2. 在本地 Codex / 桌面 Work 安装

以下使用默认个人插件市场。`~` 在 Windows 上是用户目录，例如 `C:/Users/你的用户名`。

1. 将下载解压或自行构建得到的 `studymate/` 整个复制到 `~/plugins/studymate/`，确认里面直接包含 `.codex-plugin/plugin.json`，不要多套一层 `studymate/`。
2. 创建 `~/.agents/plugins/marketplace.json`，内容如下。如果文件已存在，保留原有 `name`、`interface` 和所有插件，只在 `plugins` 数组中添加 StudyMate 条目；已有同名条目时核对其来源，不要重复添加。

```json
{
  "name": "personal",
  "interface": {
    "displayName": "Personal"
  },
  "plugins": [
    {
      "name": "studymate",
      "source": {
        "source": "local",
        "path": "./plugins/studymate"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

这里的 `source.path` 相对个人市场根目录 `~`，不是相对 `.agents/plugins/`。默认个人市场由客户端发现，无须运行 `codex plugin marketplace add`。

3. 重启桌面客户端，在插件目录选择个人市场并安装 **StudyMate**，随后新建任务。也可以请内置插件创建器完成上面的目录接入：

```text
$plugin-creator 请将已有的 ~/plugins/studymate 插件接入默认个人插件市场，保留其他插件和市场名称，校验后让我在插件目录安装。
```

桌面 Work 中用 `@plugin-creator`。完整格式及本地市场行为见 [OpenAI：Package your plugin](https://developers.openai.com/plugins/build/plugins)。

## 3. 选择学习工作区并开始

课件生成和完整校验需要 **Python 3.9+、PyYAML、jsonschema**，依赖应安装在宿主实际使用的 Python 环境中：

```bash
python -m pip install pyyaml jsonschema
```

macOS / Linux 若命令为 `python3`，替换上述 `python` 即可。插件安装目录可能位于客户端缓存中；把课件和学习记录放在独立、可写的目录，例如 `D:/StudyMate-workspace` 或 `~/StudyMate-workspace`。

在新任务中选择 StudyMate 的 `learning-system` 技能并发送：

```text
我想用 StudyMate 学线性代数。我学过高中数学，每周有 4 小时。
学习工作区使用 D:/StudyMate-workspace，请先了解我的目标，再设计课程。
```

Codex 可通过 `$` 选择技能，ChatGPT 可通过 `@` 选择；以客户端列表中的实际技能名称为准。后续说「继续上次的科目」「考考我」或「这里没懂」即可。技能调用方式见 [OpenAI：Skills & Plugins](https://learn.chatgpt.com/docs/skills-and-plugins)。

总控会在工作区恢复进度、生成课程大纲和 HTML 课件，主页位于 `<工作区>/index.html`。学习数据应整体保留，包括隐藏的 `.learning/` 目录；插件升级与学习数据分开管理。

脚本也支持以下定位方式，优先级从上到下：

1. 显式工作区参数，例如 `python scripts/gen_home.py "D:/StudyMate-workspace"`。
2. 环境变量 `STUDYMATE_WORKSPACE`。
3. 兼容环境变量 `LEARN_WORKSPACE`。
4. `STUDYMATE_CONFIG` 指向的 YAML 文件中的 `workspace` 字段；未设置时兼容原有 DSH 配置。

配置文件最小内容如下，无需 DSH 的 `root` 字段：

```yaml
workspace: "D:/StudyMate-workspace"
```

环境变量要在执行脚本的宿主进程中可见。在对话中明确工作区路径通常最直接。手动运行生成器前先创建该目录，并从插件根目录执行命令；也可使用脚本的绝对路径。

## 4. Codex 中的连续选择与续学

日常使用只需选择 **StudyMate · 学习总控**。课程设计、讲解、出题等五个角色由总控调度，避免多个角色各自询问同一件事；直接选择某个角色时也会先接回已有学习流程。

- 一次说明的目标、基础、时间和偏好会一并采纳，只补真正缺失的选项，不再从头盘问。
- 支持提问卡片的宿主会优先使用卡片；一次一个决策，收到选择后直接进入下一项或开始执行，不反复问“开始吗”。没有可用卡片工具或当前模式不支持时，使用普通对话，回复选项或自由文字都可以。
- 弹窗仍在等回答时，不会把默认高亮当成已选择，也不会生成依赖该选择的课程。教学题目仍在课件或对话中作答，避免推荐选项透露答案。
- “继续线代”“刚才那个例子没懂”“换成 Python”“今天到这”分别接到续学、局部答疑、科目切换和保存暂停，不重启整套盘问。
- 工作区会保存当前科目、节点、阶段、已回答选择和待问项。应用重开后先核对这些断点及真实课件；课程已有的进度、作品和评估记录继续保留。状态仅记录流程，不能把看过页面或说“懂了”当成掌握证据。

例如：

```text
我想学 Python 做 CSV 报表，零基础，每周 4 小时。
项目和课件形式按你推荐，直接开始第一课。
```

这时总控应直接采用已给的信息，只在确有影响的歧义处询问。卡片能力和异步回传由客户端提供，插件无法保证每个 Codex / ChatGPT 界面都有同样的弹窗。断点保存在学习工作区的 `.learning/interaction.json`，备份工作区时随隐藏目录一起保留。

## 5. ChatGPT 网页端

本地个人市场中的文件路径不会自动变成网页端可用的插件。网页端需要通过账户或工作区支持的插件导入、发布入口接收完整包；能否看到这些入口取决于当前产品功能和管理员设置。

若账户提供插件 ZIP 导入入口，选择 `studymate-openai.zip`，检查导入结果并安装，再新建 **Work** 对话，选择 `learning-system`。StudyMate 的完整工作流需要可执行 Python、读写文件的环境。云端工作区使用该环境内的可写路径；本机 `D:/...` 不会自动同步过去。需要续学时应把学习工作区文件一并带入，并及时导出保存。

公开分发由维护者另行完成：在 OpenAI 插件提交门户选择 **Create plugin → Skills only**，上传完整 ZIP，补充发布资料并接受审核；批准后还需执行发布。生成 ZIP 或提交草稿都不代表插件已经在公共目录可用。详见 [OpenAI：Submit plugins](https://developers.openai.com/plugins/deploy/submission) 与 [ZIP 格式及校验要求](https://developers.openai.com/plugins/deploy/submission-errors)。

## 更新与排查

- **安装后没有技能**：确认安装的是完整插件；重启客户端并新建任务，在技能列表查找 `learning-system`。
- **本地改动未生效**：重新构建并更新市场指向的源目录，再请 `$plugin-creator` 按本地插件更新流程刷新版本缓存并重新安装，随后新建任务。不要直接修改客户端缓存。
- **提示缺少 yaml / schema 校验被跳过**：在执行脚本的同一 Python 环境安装 `pyyaml` 和 `jsonschema`。
- **提示没有工作区**：给出明确的可写目录，或配置上述环境变量。OpenAI 版本不要求先运行 DSH 安装脚本。
- **宿主没有联网或子代理**：按现有资料与可用工具执行；角色可以顺序完成，缺失的来源、图片或运行验证应如实说明。

日常课程结构与课件写法仍见 [使用说明](使用说明.md) 和 [课件内容格式](课件内容格式.md)；其中 DSH 专属的预设安装部分不适用于本插件。
