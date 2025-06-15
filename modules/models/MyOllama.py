# 导入所需库
import socket

import requests  # 用于发送HTTP请求
import json  # 用于JSON数据解析和序列化
from typing import List, Tuple, Generator, Dict, Any, Optional  # 类型提示支持


class OllamaClient:
    """Ollama API客户端封装"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        初始化Ollama客户端

        Args:
            base_url: API基础URL (默认 http://localhost:11434)
        """
        self.base_url = base_url  # 存储API基础URL
        self.models_endpoint = f"{base_url}/api/tags"  # 模型列表API端点
        self.chat_endpoint = f"{base_url}/api/chat"  # 聊天API端点

    def get_local_models(self) -> List[str]:
        """获取本地可用模型列表"""
        try:
            # 发送GET请求获取模型列表
            response = requests.get(self.models_endpoint)
            response.raise_for_status()  # 检查HTTP错误
            data = response.json()  # 解析JSON响应
            # 从响应中提取模型名称列表
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException as e:
            # 网络请求错误处理
            print(f"模型获取失败: {str(e)}")
            # 返回默认模型列表
            return ["llama3", "mistral"]
        except (json.JSONDecodeError, KeyError) as e:
            # JSON解析或键值错误处理
            print(f"响应解析失败: {str(e)}")
            return []

    def generate_response(
            self,
            message: str,  # 用户当前输入
            history: List[Tuple[str, str]],  # 对话历史记录
            model_name: str,  # 使用的模型名称
            use_stream: bool = True  # 是否使用流式响应
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
        # 格式化对话历史为API所需的格式
        messages = self._format_messages(message, history)

        # 构造API请求负载
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": use_stream
        }

        try:
            if use_stream:
                # 流式模式：使用生成器返回逐块响应
                yield from self._stream_response(payload)
            else:
                # 非流式模式：直接返回完整响应
                yield self._full_response(payload)
        except Exception as e:
            # 异常处理
            yield f"请求失败: {str(e)}"

    def _format_messages(self, message: str, history: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """将对话历史格式化为API所需格式"""
        messages = []
        # 遍历历史对话记录
        for human, assistant in history:
            # 添加用户消息
            messages.append({"role": "user", "content": human})
            # 添加AI回复
            messages.append({"role": "assistant", "content": assistant})
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        return messages

    def _stream_response(self, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """处理流式响应"""
        # 发送流式POST请求
        with requests.post(self.chat_endpoint, json=payload, stream=True) as response:
            response.raise_for_status()  # 检查HTTP错误
            partial_message = ""  # 存储部分消息
            # 逐行读取流式响应
            for line in response.iter_lines():
                if line:
                    # 解析JSON响应块
                    chunk = json.loads(line.decode('utf-8'))
                    if "message" in chunk and "content" in chunk["message"]:
                        content = chunk["message"]["content"]  # 获取内容
                        partial_message += content  # 追加到部分消息
                        yield partial_message  # 生成当前完整消息

    def _full_response(self, payload: Dict[str, Any]) -> str:
        """处理非流式响应"""
        response = requests.post(self.chat_endpoint, json=payload)  # 发送普通请求
        response.raise_for_status()  # 检查HTTP错误
        # 返回完整响应消息内容
        return response.json()["message"]["content"]


# 主程序入口
if __name__ == "__main__":
    # 导入Gradio库 - 用于构建Web UI界面
    import gradio as gr

    # 创建客户端实例
    client = OllamaClient()

    # 创建Gradio界面
    with gr.Blocks(title="Ollama 本地对话") as app:
        # 标题区域
        gr.Markdown("## 🦙 Ollama 本地大模型对话系统")

        # 模型选择区域
        models = client.get_local_models()  # 获取初始模型列表
        with gr.Row():  # 创建行布局
            # 模型下拉选择器
            model_dropdown = gr.Dropdown(
                choices=models,  # 选项列表
                value=models[0] if models else "",  # 默认值
                label="选择模型",  # 标签文本
                interactive=True  # 允许用户交互
            )
            # 刷新按钮
            refresh_btn = gr.Button("🔄 刷新模型列表")

        # 聊天显示区域
        chatbot = gr.Chatbot(height=500)  # 设置聊天机器人组件高度
        # 用户输入框
        msg = gr.Textbox(label="输入问题", placeholder="在这里输入您的问题...")

        # 控制按钮区域
        with gr.Row():  # 创建行布局
            submit_btn = gr.Button("🚀 提交")  # 提交按钮
            clear_btn = gr.Button("🧹 清除对话")  # 清除对话按钮
            stream_toggle = gr.Checkbox(label="流式响应", value=True)  # 流式模式开关

        # 模型刷新功能
        def refresh_models():
            """刷新模型列表回调函数"""
            new_models = client.get_local_models()
            # 更新下拉框的选项和值
            return gr.Dropdown.update(
                choices=new_models,
                value=new_models[0] if new_models else None
            )

        # 绑定刷新按钮事件
        refresh_btn.click(
            refresh_models,  # 触发函数
            inputs=[],  # 输入参数列表
            outputs=[model_dropdown]  # 输出组件
        )

        # 消息处理函数
        def process_message(message, history, model_name, use_stream):
            """处理用户消息并生成AI响应"""
            # 调用生成响应方法，同时跟踪当前消息
            for response in client.generate_response(
                    message,
                    history,
                    model_name,
                    use_stream
            ):
                # 构建新的聊天历史（包含当前生成的响应）
                yield [(user, resp) if i != len(history) else (user, response)
                       for i, (user, resp) in enumerate(history + [(message, response)])]

        # 绑定消息提交事件（回车提交）
        msg.submit(
            lambda: None,  # 占位函数（立即触发）
            None,  # 无输入
            None  # 无输出
        ).then(
            process_message,  # 主处理函数
            [msg, chatbot, model_dropdown, stream_toggle],  # 输入参数
            [chatbot],  # 输出组件
        ).then(lambda: "", None, [msg])  # 清空输入框

        # 绑定提交按钮点击事件
        submit_btn.click(
            lambda: None,  # 占位函数
            None,
            None
        ).then(
            process_message,  # 主处理函数
            [msg, chatbot, model_dropdown, stream_toggle],
            [chatbot],
        ).then(lambda: "", None, [msg])  # 清空输入框

        # 绑定清除对话按钮
        clear_btn.click(
            lambda: [],  # 返回空列表
            None,  # 无输入
            chatbot  # 输出到聊天组件（重置历史）
        )
    # 启动应用
    app.launch(
        server_name="0.0.0.0", # 允许所有网络接口
        # server_name=server_name,  # 本地主机地址
        server_port=7960,  # 服务端口号
        share=False  # 不生成公开链接
    )