import gradio as gr


def calculate(x, y, operation):
    """根据下拉框选择进行实时计算（单选模式）"""
    if operation == "和":
        return f"和: {x + y}"
    elif operation == "差":
        return f"差: {x - y}"
    else:
        return "请选择运算类型"


# 创建实时响应界面
with gr.Blocks() as demo:
    with gr.Row():
        x_input = gr.Number(label="数字 X", value=0)
        y_input = gr.Number(label="数字 Y", value=0)

    # 核心修改：使用下拉单选组件
    operation_dropdown = gr.Dropdown(
        choices=["和", "差"],  # 可选项
        label="选择运算类型",
        value=None,  # 初始不选任何项
        interactive=True
    )

    # 输出区域（自动响应变化）
    output = gr.Textbox(label="计算结果", interactive=False)

    # 绑定所有组件的变更事件（输入框+下拉框）
    for component in [x_input, y_input, operation_dropdown]:
        component.change(
            fn=calculate,
            inputs=[x_input, y_input, operation_dropdown],
            outputs=output
        )

demo.launch()