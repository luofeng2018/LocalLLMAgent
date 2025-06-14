from __future__ import annotations

import logging
import os

import colorama
import commentjson as cjson

from modules import config

from ..index_func import *
from ..presets import *
from ..utils import *
from .base_model import BaseLLMModel, ModelType


def get_model(
    model_name,
    lora_model_path=None,
    access_key=None,
    temperature=None,
    top_p=None,
    system_prompt=None,
    user_name="",
    original_model = None
) -> BaseLLMModel:
    msg = i18n("模型设置为了：") + f" {model_name}"
    model_type = ModelType.get_type(model_name)
    lora_selector_visibility = False
    lora_choices = ["No LoRA"]
    dont_change_lora_selector = False
    if model_type != ModelType.OpenAI:
        config.local_embedding = True
    # del current_model.model
    model = original_model
    try:
        if model_type == ModelType.OpenAIVision or model_type == ModelType.OpenAI:
            logging.info(f"正在加载 OpenAI 模型: {model_name}")
            from .OpenAIVision import OpenAIVisionClient
            access_key = os.environ.get("OPENAI_API_KEY", access_key)
            model = OpenAIVisionClient(
                model_name, api_key=access_key, user_name=user_name)
        elif model_type == ModelType.LLaMA and lora_model_path == "":
            msg = f"现在请为 {model_name} 选择LoRA模型"
            logging.info(msg)
            lora_selector_visibility = True
            if os.path.isdir("lora"):
                lora_choices = ["No LoRA"] + get_file_names_by_pinyin("lora", filetypes=[""])
        elif model_type == ModelType.Ollama:
            from .Ollama import OllamaClient
            ollama_host = os.environ.get("OLLAMA_HOST", access_key)
            model = OllamaClient(model_name, user_name=user_name, backend_model=lora_model_path)
            model_list = model.get_model_list()
            lora_selector_visibility = True
            lora_choices = [i["name"] for i in model_list["models"]]
        elif model_type == ModelType.Unknown:
            raise ValueError(f"Unknown model: {model_name}")
        else:
            raise ValueError(f"Unimplemented model type: {model_type}")
        logging.info(msg)
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = f"{STANDARD_ERROR_MSG}: {e}"
    modelDescription = i18n(model.description)
    presudo_key = hide_middle_chars(access_key)
    if original_model is not None and model is not None:
        model.history = original_model.history
        model.history_file_path = original_model.history_file_path
        model.system_prompt = original_model.system_prompt
    if dont_change_lora_selector:
        return model, msg, gr.update(label=model_name, placeholder=setPlaceholder(model=model)), gr.update(), access_key, presudo_key, modelDescription, model.stream
    else:
        return model, msg, gr.update(label=model_name, placeholder=setPlaceholder(model=model)), gr.Dropdown(choices=lora_choices, visible=lora_selector_visibility), access_key, presudo_key, modelDescription, model.stream


if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        openai_api_key = cjson.load(f)["openai_api_key"]
    # set logging level to debug
    logging.basicConfig(level=logging.DEBUG)
    # client = ModelManager(model_name="gpt-3.5-turbo", access_key=openai_api_key)
    client = get_model(model_name="chatglm-6b-int4")
    chatbot = []
    stream = False
    # 测试账单功能
    logging.info(colorama.Back.GREEN + "测试账单功能" + colorama.Back.RESET)
    logging.info(client.billing_info())
    # 测试问答
    logging.info(colorama.Back.GREEN + "测试问答" + colorama.Back.RESET)
    question = "巴黎是中国的首都吗？"
    for i in client.predict(inputs=question, chatbot=chatbot, stream=stream):
        logging.info(i)
    logging.info(f"测试问答后history : {client.history}")
    # 测试记忆力
    logging.info(colorama.Back.GREEN + "测试记忆力" + colorama.Back.RESET)
    question = "我刚刚问了你什么问题？"
    for i in client.predict(inputs=question, chatbot=chatbot, stream=stream):
        logging.info(i)
    logging.info(f"测试记忆力后history : {client.history}")
    # 测试重试功能
    logging.info(colorama.Back.GREEN + "测试重试功能" + colorama.Back.RESET)
    for i in client.retry(chatbot=chatbot, stream=stream):
        logging.info(i)
    logging.info(f"重试后history : {client.history}")
    # # 测试总结功能
    # print(colorama.Back.GREEN + "测试总结功能" + colorama.Back.RESET)
    # chatbot, msg = client.reduce_token_size(chatbot=chatbot)
    # print(chatbot, msg)
    # print(f"总结后history: {client.history}")
