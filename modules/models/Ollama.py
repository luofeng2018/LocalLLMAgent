from ollama import Client

from modules.presets import i18n
from .base_model import BaseLLMModel
from ..utils import count_token


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



# class OllamaClient(BaseLLMModel):
#     def __init__(self, model_name, user_name="", ollama_host="", backend_model="") -> None:
#         super().__init__(model_name=model_name, user=user_name)
#         self.backend_model = backend_model
#         self.ollama_host = ollama_host
#         self.update_token_limit()
#
#     def get_model_list(self):
#         client = Client(host=self.ollama_host)
#         return client.list()
#
#     def update_token_limit(self):
#         lower_model_name = self.backend_model.lower()
#         if "mistral" in lower_model_name:
#             self.token_upper_limit = 8*1024
#         elif "gemma" in lower_model_name:
#             self.token_upper_limit = 8*1024
#         elif "codellama" in lower_model_name:
#             self.token_upper_limit = 4*1024
#         elif "llama2-chinese" in lower_model_name:
#             self.token_upper_limit = 4*1024
#         elif "llama2" in lower_model_name:
#             self.token_upper_limit = 4*1024
#         elif "mixtral" in lower_model_name:
#             self.token_upper_limit = 32*1024
#         elif "llava" in lower_model_name:
#             self.token_upper_limit = 4*1024
#
#     def get_answer_stream_iter(self):
#         if self.backend_model == "":
#             return i18n("请先选择Ollama后端模型\n\n")
#         client = Client(host=self.ollama_host)
#         response = client.chat(model=self.backend_model, messages=self.history,stream=True)
#         partial_text = ""
#         for i in response:
#             response = i['message']['content']
#             partial_text += response
#             yield partial_text
#         self.all_token_counts[-1] = count_token(partial_text)
#         yield partial_text
