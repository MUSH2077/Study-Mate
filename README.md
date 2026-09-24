<p align="center"><img src="docs/images/logo.png" width="120" alt="StudyMate"></p>

<h1 align="center">StudyMate</h1>

<p align="center"><b>你的AI学习搭档：定计划、讲知识、做项目，学透一门科目</b></p>

<p align="center">
<img src="https://img.shields.io/badge/version-v0.1-1c5a40" alt="版本 v0.1">
<img src="https://img.shields.io/badge/DSH-%E5%AD%A6%E4%B9%A0%E6%A8%A1%E5%BC%8F%E9%A2%84%E8%AE%BE-1c5a40" alt="DSH 学习模式预设">
<img src="https://img.shields.io/badge/python-3.9%2B-3776ab" alt="Python">
<img src="https://img.shields.io/github/license/Miaotofu01/Study-Mate" alt="MIT License">
</p>

<p align="center"><sub> StudyMate 是面向数学与计算机科目学习的助手，原则是「learn with doing」</sub></p>

<p align="center"><a href="#快速开始">快速开始</a> · <a href="#它是什么">它是什么</a> · <a href="#核心功能">核心功能</a> · <a href="#常见问题">常见问题</a> · <a href="docs/使用说明.md">使用说明</a></p>

<p align="center"><img src="docs/images/taitou.png" width="860" alt="StudyMate：看板娘 + 手写体品牌字 + 覆盖科目（线代／微积分／概率论／C++／Python／机器学习／深度学习）+「任何科目，一站式搞定 / Learn With Doing」"></p>

## 前言

本项目原先是vibe出来给自己用的一个小项目，没想到有这么多人喜欢。但是vibe出来的东西有很多的问题，包括但不限于「文档过于臃肿且充满AI味、可读性极差」、「海量且无用的防御性代码」、「混乱的功能模块」。

虽然现在跑起来的效果也不差，但是跟我理想中的效果还是有很大差距

我觉得这样的东西对不起这么多的信任与star，我会直视这些问题，并且人工修改审查每一个文件，在未来的更新维护中给大家带来更好的体验，感谢大家的使用与支持，有任何建议都可以提个issue，本项目将长期维护。

## 快速开始

下面是 DSH 的安装方式。Codex 和 ChatGPT Work 用户请看 [OpenAI 插件快速开始](#codex-和-chatgpt-work)。

**依赖**：DSH、Python 3.9+、pyyaml、bash、coreutils、sed（Windows 只要 DSH + Python 3.9+ + pyyaml）

**通过 npm 安装（推荐）**

更新也可使用以下命令，原生命令安装见 [安装说明](docs/安装.md)。

```bash
npx @yunmiao/studymate@latest install
dsh web
```

**macOS / Linux**

```bash
# ① 克隆本项目
git clone https://github.com/Miaotofu01/Study-Mate.git StudyMate && cd StudyMate
# ② 装「学习模式」预设 + 建学习工作区
./install.sh
# ③ 启动 DSH，在任意目录新建会话并选「学习模式」预设
dsh web
```

**Windows（PowerShell）**

```powershell
git clone https://github.com/Miaotofu01/Study-Mate.git StudyMate; cd StudyMate
powershell -ExecutionPolicy Bypass -File .\install.ps1
dsh web
```

安装脚本成功运行的结果：

```text
① 预设 → /home/you/.dsh/.agent-presets/learning（skill 目录：/path/to/StudyMate/.dsh/skills）
② 学习工作区 → /path/to/StudyMate/workspace（配置在 /home/you/.dsh/studymate-config.yaml）
完成（StudyMate v0.1）。现在可在任意目录开会话，选'学习模式'预设开始学习。
```

- **第一次学习**：新建会话时选「学习模式」，说一句「我想学 [某个科目]」。
- **学习工作区默认在 StudyMate/workspace，所有课件与记忆均存放在工作区**
- 第一次生成课程后，课程主页在工作区目录 `<workspace>/index.html`，是未来所有课件的入口

<details>
<summary><b><code>install.sh</code> / <code>install.ps1</code> 具体做了什么 / 怎么换工作区位置</b></summary>

两个脚本做同样两件事：把 `preset/learning/` 装到 `~/.dsh/.agent-presets/learning/`，并让预设里的技能目录固定指向本项目的 `.dsh/skills/`；建学习工作区（默认本项目的 `workspace/`）并把它的路径写进 `~/.dsh/studymate-config.yaml`。

换工作区位置：改 `~/.dsh/studymate-config.yaml` 里的 `workspace:`，或跑一次 `LEARN_WORKSPACE=<新路径> ./install.sh`（Windows：`$env:LEARN_WORKSPACE='D:\study'; .\install.ps1`）；项目被移动过也要重跑一次（配置里的 `root` 会按当前位置重写）。学习数据都在工作区里，换机器把整个项目（含 `workspace/`）拷走再跑一次安装脚本。

</details>

## Codex 和 ChatGPT Work

从 [GitHub Releases](https://github.com/Miaotofu01/Study-Mate/releases) 下载支持 OpenAI 的版本所附 `studymate-openai.zip`，按 [安装说明](docs/Codex与ChatGPT.md) 安装。ZIP 内含 11 个技能、课件引擎和模板。

DSH 用户沿用上面的 npm 安装方式；Codex / ChatGPT Work 用户下载 ZIP。两种产物共用代码和版本，每次 Release 一起发布。

开发者在源码仓库中也可自行构建：

```bash
npm run build:plugin
```

生成 `dist/studymate/`（完整插件目录）和 `dist/studymate-openai.zip`（分发包）。构建命令只生成文件；正式分发由仓库的 [Release 流程](docs/releasing.md) 完成。

安装后，在新任务中选择 StudyMate 的 `learning-system` 技能，说「我想学线性代数，学习工作区用 `D:/StudyMate-workspace`」。完整的课件生成与校验需要 Python 3.9+、PyYAML 和 jsonschema；工作区应放在插件目录之外。

## 它是什么

StudyMate 是一套**数学/计算机学习工作流、SKILL 与 HTML 课件引擎**，支持 DSH（DeepSeek Harness）的「学习模式」预设，也可打包为 Codex 和 ChatGPT Work 插件。它按需组织收集资料、采图、课程设计、讲解、练习评估五个角色；宿主支持时可委派给子代理，否则依次完成各角色工作。

- **课程组成：讲解|练习|项目实操**：每门课一份大纲——知识点按前置依赖排成路线图，每个知识点标课的类型「概念课 | 实操课 | 实验课」（大纲里写 `概念`／`实操`／`实验`）。学习进度落在文件里，每次新对话可继承已有进度。
- **跨科目共享记忆**：记住你的现有水平、哪种讲法有效、常见卡点，下一门课不用重新自我介绍。

## 为什么用它

| 常见做法         | 卡在哪                                           | StudyMate 的做法                                                                     |
| ---------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------ |
| 直接跟 AI 聊天学 | 会话一长上下文就吃不下；聊完不留痕，下次从零开始 | 信息与偏好由记忆文件保存；每次会话只带相关记忆、上下文短；课件是教科书式的讲解与配图 |
| 看视频课 / 网课  | 质量参差不齐；付费；无法跟随前沿发展的节奏       | 讲解方式定制化；收集最新的资料与标准；完全开源                                       |


## 核心功能

**课程总览与大纲路线图**：总览页列全部科目与当前节点，点进去是那门课的知识点路线图，按依赖分层排开、按状态着色，点节点原地展开课件子卡片。

<img src="docs/images/preview-index.png" width="640" alt="路线图示例">

**课件是学习的主载体**：经典教材的讲解风格，丰富的配图，定制化的题目与项目目标。

<img src="docs/images/preview-lesson.png" width="640" alt="课件示例">

想翻一遍真实产出：仓库里的 [`examples/`](examples/) 是一份完整示例工作区（**线性代数** + **计算机网络**），页面已经渲染入库——clone 下来用浏览器打开 `examples/index.html`，就能一路点到科目主页与课件。


## 用法示例

- **「我想学 C++ 打竞赛」** → 先盘问目的/程度/项目/实验方式，再产出大纲路线图与科目主页，开第一课。
- **贴一段看不懂的课文 + 「这里没懂」** → 主教练当场答一小段，记一条档案，送你回原位接着读。
- **「考考我」** → 现场出题 + 按可运行证据核验，给一份评估记录并更新进度。
- **「太简单了 / 没听懂」** → 换讲法（加边界与反例，或降一层抽象），并把这条偏好记进共享记忆。
  
<img src="docs/images/preview-chat.png" width="640" alt="对话示例">

## 配置与维护

<details>
<summary><b>脚本：主页生成 + 课件渲染 + 四道校验</b></summary>

```bash
python3 scripts/gen_home.py                    # 生成根主页 + 全部科目主页（默认读配置里的 workspace）
python3 scripts/preview_templates.py --open    # 用假数据渲染主页模板到 .preview/，只看样式与交互
python3 scripts/render_lesson.py <subject_path> <节点id>   # 内容文件 + 题库 → 课件 HTML（--check 只校验不写盘）
python3 scripts/check_curriculum.py examples/.learning/subjects/computer-networks/curriculum.yaml
python3 scripts/check_lesson.py examples/.learning/subjects/linear-algebra/lessons/0001-vector.space.html --subject examples/.learning/subjects/linear-algebra --node vector.space
python3 scripts/check_pool.py <你的科目目录>    # 图片池：索引 pool.md 与 assets/img/pool/ 对不对得上
python3 scripts/check_skill.py .dsh/skills/*    # 技能 frontmatter（改过技能就跑一次）
bash scripts/tests/run_tests.sh                # 回归测试：检查/题目属性/命名指针/提示词规则/DOM（改引擎就跑一次）

# 换成你自己的科目：--subject 给科目目录，--node 给该课件对应的节点 id；大纲校验可一次传多个 curriculum.yaml
```

`check_lesson.py` 只阻断工程与结构缺项（文件名与编号、课件归属、共享层引用、**本地引用可达**、题目结构与属性写法、题目位置标记残留、主题开关；`kind` 为 `实操/实验` 时还要求 lab 与产物齐全），内容风格类问题只提示；其中「题目位置标记残留」只可能来自手写时代的老课件——渲染产物里不会有标记。`check_pool.py` 校验图片池：索引表头七列、文件名合规、来源 URL 与许可非空、单张 ≤500 KB——还没建过图片池的科目没有 `assets/img/pool.md`，它会报一行「索引不存在」并退出 1，那是图片库还没建，不是命令坏了。退出码：`check_lesson.py` / `check_curriculum.py` / `check_pool.py` 有阻断项即 1，`gen_home.py` 占位符缺失或产物断链即 1。

`scripts/tests/run_tests.sh` 不需要浏览器（`--browser` 才加真实 Chrome 的高亮那套）；测试自己造临时科目，不碰 `workspace/`。改了检查、`templates/assets/` 或 `.dsh/skills/` 之后跑一次，见 `scripts/tests/README.md`。

</details>

## 项目结构

```text
StudyMate/                     ← 本仓库：系统源码（引擎），学习时只读
├── install.sh / install.ps1   # 装预设 + 建学习工作区，幂等（macOS/Linux 与 Windows 各一份）
├── .dsh/skills/               # 11 个技能：总控 learning-system + 5 个角色 + 5 个规范
│   ├── learning-system/       #   总控（主教练）：开场、盘问、调度、档案
│   ├── resource-scout/        #   角色：收集资料（权威教材与官方文档 → 资源清单）
│   ├── image-scout/           #   角色：采图（抓网页现成的图 → 科目图片库与索引）
│   ├── curriculum-designer/   #   角色：课程设计（大纲 / 实验课节点）
│   ├── learning-coach/        #   角色：讲解（写课件内容）
│   ├── practice-evaluator/    #   角色：出题与评估（题目唯一 owner）
│   ├── lesson-design/         #   规范：课件唯一约束来源
│   ├── layered-practice/      #   规范：四层练习与题型
│   ├── evidence-check/        #   规范：完成证据核验
│   ├── local-qa/              #   规范：局部提问怎么答
│   └── record-keeping/        #   规范：学习状态读写规则
├── preset/learning/           # 「学习模式」预设源（安装脚本装到 ~/.dsh/）
├── schemas/                   # 5 份数据结构：大纲 / 进度 / 评估 / 会话摘要 / 科目
├── templates/                 # 页面骨架（主页、科目页、课件壳）与前端资源 assets/
├── scripts/                   # 主页生成 + 课件渲染器 + 四道校验检查（用法见上）+ tests/ 回归测试
├── dist/studymate/            # build:plugin 生成的 OpenAI 插件，含适配后的 11 个技能（不入库）
├── examples/                  # 示例学习工作区：线性代数 + 计算机网络，页面已生成，clone 即可点开
├── docs/                      # 使用说明、课件内容格式、设计方案、工程约束、文件归属、docs/images/ 截图
└── workspace/                 # 你的学习数据（默认位置，可配置；也被 .gitignore 忽略）
```

仓库之外还有一处安装落点：`~/.dsh/.agent-presets/learning/`（预设）与 `~/.dsh/studymate-config.yaml`（工作区定位），都由安装脚本写入。

学习工作区里面长什么样（科目文件夹、课件、lab、档案、课型与题型、模板与生成器的契约），见 [使用说明 §六](docs/使用说明.md#六学习数据存在哪)。

## 常见问题

<details>
<summary><b>装完没有主页 / 直接打开 <code>templates/</code> 里的 HTML 没样式</b></summary>

主页要从学习数据生成：跑 `python3 scripts/gen_home.py` 再看 `<workspace>/index.html`（还没科目时是空状态页）。`templates/*.html` 引用的是生成后的工作区相对路径，单独打开只有裸 HTML，这是设计如此。
</details>

<details>
<summary><b>报 <code>ModuleNotFoundError: No module named 'yaml'</code></b></summary>

`pip install pyyaml` 即可：主页生成与课件检查都要它。注意依赖缺了检查会**变松**——没有 `pyyaml` 时 `check_lesson.py` 跳过「这课该不该有 lab」的判定（只 `WARN`）；没有 `jsonschema` 时 `check_curriculum.py` 跳过 schema 校验，只报重复 id、悬空引用与环。
</details>

更多问题（手改 YAML 的坑、大纲改节点后指针为什么会错、能不能离线）见 [使用说明 §八 常见问题](docs/使用说明.md#八常见问题)。

## 贡献 / License

- **项目交流群**(QQ)：161914370
- **变更日志**：[CHANGELOG.md](CHANGELOG.md)
- **文档**：[使用说明](docs/使用说明.md)（日常怎么用、课型与题型、检查与档案规则）· [Codex 与 ChatGPT](docs/Codex与ChatGPT.md)（OpenAI 插件构建、安装与工作区）· [课件内容格式](docs/课件内容格式.md)（内容文件与题目位置的语法）· [文件归属](docs/文件归属.md)（代称 ↔ 路径 ↔ 维护者）· [设计方案](docs/设计方案.md)（产品视角）· [工程约束](docs/工程约束.md)（目录约定、占位符契约、脚本一览、技术选型）· [模板说明](templates/README.md) · [前端资源契约](templates/assets/README.md)

### 提改动前先跑这几条

四条校验器各管一段（最后一行是回归套件），都是确定性的、带行号报错：

```bash
python3 scripts/check_skill.py .dsh/skills/*                                   # 提示词与技能：契约、单一 owner、措辞闸门
python3 scripts/check_curriculum.py <学习工作区>/.learning/subjects/<slug>/curriculum.yaml  # 大纲：schema、引用完整、无环、实验课要写 prerequisites
python3 scripts/check_lesson.py <课件.html> --subject <科目目录> --node <节点 id>   # 课件：版式、配图、题目、命名与上下节课指针
python3 scripts/check_pool.py <科目目录>                                        # 图片库：索引七列、图片存在、命名合规、单张 ≤500 KB
bash scripts/tests/run_tests.sh                                               # 回归：11 套快测（--browser 再加 2 套，共 13 套）
```

### License

MIT（见 [LICENSE](LICENSE)，版权 Cattofu）。

## Star 趋势

<p align="center">
  <a href="https://star-history.com/#miaotofu01/study-mate&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=miaotofu01/study-mate&type=date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=miaotofu01/study-mate&type=date" />
      <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=miaotofu01/study-mate&type=date" />
    </picture>
  </a>
</p>


