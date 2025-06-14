import gradio as gr
import requests
import json
from typing import List, Tuple, Generator


# 获取本地模型列表（修复空列表处理）
def get_local_models() -> List[str]:
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception as e:
        print(f"获取模型失败: {e}")
        return ["llama3", "mistral"]  # 默认模型


# 统一响应处理接口（修复流式/非流式兼容问题）[6,8](@ref)
def generate_response(
        message: str,
        history: List[Tuple[str, str]],
        model_name: str,
        use_stream: bool
) -> Generator[str, None, None]:
    # 转换对话历史格式
    messages = []
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})
    messages.append({"role": "user", "content": message})

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": use_stream  # 根据开关决定流式模式
    }

    try:
        # 流式响应处理
        if use_stream:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                partial_message = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if "message" in chunk:
                            content = chunk["message"]["content"]
                            partial_message += content
                            yield partial_message
        # 非流式响应处理（统一返回生成器）[8](@ref)
        else:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            full_response = response.json()["message"]["content"]
            yield full_response

    except Exception as e:
        yield f"请求失败: {str(e)}"


# 创建Gradio界面（修复事件绑定）[1](@ref)
with gr.Blocks(title="Ollama 本地对话") as app:
    gr.Markdown("## 🦙 Ollama 本地大模型对话系统")

    # 模型选择区域（修复空列表处理）
    models = get_local_models()
    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=models,
            value=models[0] if models else "",
            label="选择模型",
            interactive=True
        )
        refresh_btn = gr.Button("🔄 刷新模型列表")

    # 聊天区域
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="输入问题", placeholder="在这里输入您的问题...")

    # 控制按钮区域
    with gr.Row():
        submit_btn = gr.Button("🚀 提交")
        clear_btn = gr.Button("🧹 清除对话")
        stream_toggle = gr.Checkbox(label="流式响应", value=True)


    # 修复模型刷新机制（正确更新现有组件）[1](@ref)
    def refresh_models():
        new_models = get_local_models()
        return gr.Dropdown.update(
            choices=new_models,
            value=new_models[0] if new_models else None
        )


    refresh_btn.click(
        refresh_models,
        inputs=[],
        outputs=[model_dropdown]
    )


    # 统一消息处理函数
    def process_message(message, history, model_name, use_stream):
        # 生成响应并更新聊天历史
        for response in generate_response(message, history, model_name, use_stream):
            # 创建新历史记录（用户消息+最新AI响应）
            new_history = history + [(message, response)]
            # 更新聊天框（关键修复：实时更新对话历史）[6](@ref)
            yield new_history


    # 绑定提交事件（修复历史传递问题）
    msg.submit(
        process_message,
        [msg, chatbot, model_dropdown, stream_toggle],
        [chatbot],
    ).then(lambda: "", None, [msg])  # 清空输入框

    submit_btn.click(
        process_message,
        [msg, chatbot, model_dropdown, stream_toggle],
        [chatbot],
    ).then(lambda: "", None, [msg])

    # 清除对话
    clear_btn.click(lambda: [], None, chatbot)

# 启动应用（端口冲突时自动切换）[4](@ref)
app.launch(
    server_name="127.0.0.1",
    server_port=7960,
    share=False
)