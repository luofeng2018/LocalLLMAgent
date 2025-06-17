from __future__ import annotations

from .OllamaVision import OllamaVisionClient
from .base_model import BaseLLMModel
from ..utils import *


def get_model(
        model_name,
        lora_model_path=None,
        access_key=None,
        temperature=None,
        top_p=None,
        system_prompt=None,
        user_name="",
        original_model=None
) -> BaseLLMModel:
    # model_name = "deepseek-r1:1.5b"
    msg = i18n("模型设置为：") + f" {model_name}"
    lora_selector_visibility = False
    lora_choices = ["No LoRA"]
    dont_change_lora_selector = False

    model = original_model
    try:
        logging.info(f"正在加载 Ollama 模型: {model_name}")
        access_key = os.environ.get("OPENAI_API_KEY", access_key)
        model = OllamaVisionClient(model_name, api_key=access_key, user_name=user_name)
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
        return model, msg, gr.update(label=model_name, placeholder=setPlaceholder(
            model=model)), gr.update(), access_key, presudo_key, modelDescription, model.stream
    else:
        return model, msg, gr.update(label=model_name, placeholder=setPlaceholder(model=model)), gr.Dropdown(
            choices=lora_choices,
            visible=lora_selector_visibility), access_key, presudo_key, modelDescription, model.stream
