<div align="right">
  <!-- 语言: -->
  简体中文 | <a title="English" href="./readme/README_en.md">English</a> | <a title="Japanese" href="./readme/README_ja.md">日本語</a> | <a title="Russian" href="./readme/README_ru.md">Russian</a> | <a title="Korean" href="./readme/README_ko.md">한국어</a>
</div>

<sup>New!</sup> 全新的用户界面！精致得不像 Gradio，甚至有毛玻璃效果！

<sup>New!</sup> 适配了移动端（包括全面屏手机的挖孔/刘海），层级更加清晰。

<sup>New!</sup> 历史记录移到左侧，使用更加方便。并且支持搜索（支持正则）、删除、重命名。

<sup>New!</sup> 现在可以让大模型自动命名历史记录（需在设置或配置文件中开启）。

<sup>New!</sup> 现在可以将 川虎Chat 作为 PWA 应用程序安装，体验更加原生！支持 Chrome/Edge/Safari 等浏览器。

<sup>New!</sup> 图标适配各个平台，看起来更舒服。

<sup>New!</sup> 支持 Finetune（微调） GPT 3.5！


## 支持模型

仅为本地内部局域网环境Ollama 部署环境下下使用QA + RAG + MCP 

## 使用技巧

### 💪 强力功能
- **助理**：类似 AutoGPT，全自动解决你的问题；
- **在线搜索**：ChatGPT 的数据太旧？给 LLM 插上网络的翅膀；
- **知识库**：让 ChatGPT 帮你量子速读！根据文件回答问题。
- **本地部署LLM**：一键部署，获取属于你自己的大语言模型。


### 🤖 System Prompt
- 通过 System Prompt 设定前提条件，可以很有效地进行角色扮演；
- 预设了Prompt模板，点击`加载Prompt模板`，先选择 Prompt 模板集合，然后在下方选择想要的 Prompt。

### 💬 基础对话
- 如果回答不满意，可以使用 `重新生成` 按钮再试一次，或者直接 `删除这轮对话`;
- 输入框支持换行，按 <kbd>Shift</kbd> + <kbd>Enter</kbd>即可；
- 在输入框按 <kbd>↑</kbd> <kbd>↓</kbd> 方向键，可以在发送记录中快速切换；
- 每次新建一个对话太麻烦，试试 `单论对话` 功能；
- 回答气泡旁边的小按钮，不仅能 `一键复制`，还能 `查看Markdown原文`；
- 指定回答语言，让 ChatGPT 固定以某种语言回答。

### 📜 对话历史
- 对话历史记录会被自动保存，不用担心问完之后找不到了；
- 多用户历史记录隔离，除了你都看不到；
- 重命名历史记录，方便日后查找；
- <sup>New!</sup> 魔法般自动命名历史记录，让 LLM 理解对话内容，帮你自动为历史记录命名！
- <sup>New!</sup> 搜索历史记录，支持正则表达式！

### 🖼️ 小而美的体验
- 自研 Small-and-Beautiful 主题，带给你小而美的体验；
- 自动亮暗色切换，给你从早到晚的舒适体验；
- 完美渲染 LaTeX / 表格 / 代码块，支持代码高亮；
- <sup>New!</sup> 非线性动画、毛玻璃效果，精致得不像 Gradio！
- <sup>New!</sup> 适配 Windows / macOS / Linux / iOS / Android，从图标到全面屏适配，给你最合适的体验！
- <sup>New!</sup> 支持以 PWA应用程序 安装，体验更加原生！

### 👨‍💻 极客功能
- <sup>New!</sup> 支持 Fine-tune（微调）gpt-3.5！
- 大量 LLM 参数可调；
- 支持更换 api-host；
- 支持自定义代理；
- 支持多 api-key 负载均衡。

### ⚒️ 部署相关
- 部署到服务器：在 `config.json` 中设置 `"server_name": "0.0.0.0", "server_port": <你的端口号>,`。
- 获取公共链接：在 `config.json` 中设置 `"share": true,`。注意程序必须在运行，才能通过公共链接访问。
- 在Hugging Face上使用：建议在右上角 **复制Space** 再使用，这样App反应可能会快一点。

## 快速上手

在终端执行以下命令：

```shell
pip install -r requirements.txt
```


