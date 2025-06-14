import requests
import json
from typing import List, Tuple, Generator, Dict, Any, Optional


class OllamaClient:
    """Ollama API客户端封装"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        初始化Ollama客户端

        Args:
            base_url: API基础URL (默认 http://localhost:11434)
        """
        self.base_url = base_url
        self.models_endpoint = f"{base_url}/api/tags"
        self.chat_endpoint = f"{base_url}/api/chat"

    def get_local_models(self) -> List[str]:
        """获取本地可用模型列表"""
        try:
            response = requests.get(self.models_endpoint)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException as e:
            print(f"模型获取失败: {str(e)}")
            # 返回默认模型列表
            return ["llama3", "mistral"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"响应解析失败: {str(e)}")
            return []

    def generate_response(
            self,
            message: str,
            history: List[Tuple[str, str]],
            model_name: str,
            use_stream: bool = True
    ) -> Generator[str, None, None]:
        """
        生成模型响应 (支持流式/非流式)

        Args:
            message: 用户输入消息
            history: 对话历史 [(用户消息, AI回复), ...]
            model_name: 使用的模型名称
            use_stream: 是否使用流式响应

        Yields:
            AI响应内容 (分块或完整)
        """
        messages = self._format_messages(message, history)

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": use_stream
        }

        try:
            if use_stream:
                yield from self._stream_response(payload)
            else:
                yield self._full_response(payload)
        except Exception as e:
            yield f"请求失败: {str(e)}"

    def _format_messages(self, message: str, history: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """将对话历史格式化为API所需格式"""
        messages = []
        for human, assistant in history:
            messages.append({"role": "user", "content": human})
            messages.append({"role": "assistant", "content": assistant})
        messages.append({"role": "user", "content": message})
        return messages

    def _stream_response(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """处理流式响应"""
        with requests.post(self.chat_endpoint, json=payload, stream=True) as response:
            response.raise_for_status()
            partial_message = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if "message" in chunk and "content" in chunk["message"]:
                        content = chunk["message"]["content"]
                        partial_message += content
                        yield partial_message

    def _full_response(self, payload: Dict[str, Any]) -> str:
        """处理非流式响应"""
        response = requests.post(self.chat_endpoint, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]


if __name__ == "__main__":
    # 以下为Gradio界面代码
    import gradio as gr

    # 创建客户端实例
    client = OllamaClient()

    # 创建Gradio界面
    with gr.Blocks(title="Ollama 本地对话") as app:
        gr.Markdown("## 🦙 Ollama 本地大模型对话系统")

        # 模型选择区域
        models = client.get_local_models()
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


        # 模型刷新功能
        def refresh_models():
            new_models = client.get_local_models()
            return gr.Dropdown.update(
                choices=new_models,
                value=new_models[0] if new_models else None
            )


        refresh_btn.click(
            refresh_models,
            inputs=[],
            outputs=[model_dropdown]
        )


        # 消息处理函数
        def process_message(message, history, model_name, use_stream):
            for response in client.generate_response(
                    message,
                    history,
                    model_name,
                    use_stream
            ):
                yield [(user, resp) if i != len(history) else (user, response)
                       for i, (user, resp) in enumerate(history + [(message, response)])]


        # 绑定消息提交事件
        msg.submit(
            lambda: None,  # 立即触发
            None,
            None
        ).then(
            process_message,
            [msg, chatbot, model_dropdown, stream_toggle],
            [chatbot],
        ).then(lambda: "", None, [msg])

        submit_btn.click(
            lambda: None,
            None,
            None
        ).then(
            process_message,
            [msg, chatbot, model_dropdown, stream_toggle],
            [chatbot],
        ).then(lambda: "", None, [msg])

        # 清除对话
        clear_btn.click(lambda: [], None, chatbot)

    # 启动应用
    app.launch(
        server_name="127.0.0.1",
        server_port=7960,
        share=False
    )