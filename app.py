# -*- coding: UTF-8 -*-
from SAMTChatbot import demo
from modules.config import server_port, share, authflag, autobrowser, dockerflag
from modules.utils import setup_wizard, auth_from_conf
from modules.webui import reload_javascript

if __name__ == "__main__":
    reload_javascript()
    setup_wizard()
    demo.queue().launch(
        allowed_paths=["web_assets"],
        blocked_paths=["config.json", "files", "models", "lora", "modules", "history"],
        server_name="0.0.0.0",  # 允许所有网络接口
        server_port=9572,
        share=share,
        auth=auth_from_conf if authflag else None,
        favicon_path="./web_assets/favicon.ico",
        inbrowser=autobrowser and not dockerflag,  # 禁止在docker下开启inbrowser
    )
