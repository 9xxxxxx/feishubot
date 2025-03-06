import json
from datetime import datetime

from getdata.get_checkgroup_efficiency import process_checkgroup_efficiency_data


def build_message(
        template_id: str,
        template_version: str,
        template_vars: dict,
) -> dict:
    """
    构造可动态配置的嵌套JSON消息

    :param receive_id: 接收方ID
    :param template_id: 模板ID
    :param template_version: 模板版本
    :param template_vars: 模板变量字典（可自由增减字段）
    :param msg_type: 消息类型，默认为 interactive
    :return: 完整消息字典
    """
    # 构造内层 content 结构
    content = {
        "type": "template",
        "data": {
            "template_id": template_id,
            "template_version_name": template_version,
            "template_variable": template_vars  # 动态变量部分
        }
    }

    # 构造完整消息
    return json.dumps(content, ensure_ascii=False)

def build_chart_data(title,value1,value2,value3,rate1,rate2,rate3):
    mock_data = [
        {
            "type": f"4小时内-{rate1}",
            "value": value1
        },
        {
            "type": f"4-8小时-{rate2}",
            "value": value2
        },
        {
            "type": f"超8小时-{rate3}",
            "value": value3
        },
    ]
    data = ({
        "type": "pie",
        "percent": "true",
        "title": {
            "text": title
        },
        "data": {
            "values": mock_data
        },
        "valueField": "value",
        "categoryField": "type",
        "outerRadius": 0.8,
        "innerRadius": 0.4,
        "padAngle": 0.6,
        "legends": {
            "visible": "true",
            "orient": "bottom",
        },
        "padding": {
            "left": 2,
            "top": 2,
            "bottom": 2,
            "right": 0
        },
        "label": {
            "visible": "true"
        },
        "pie": {
            "style": {
                "cornerRadius": 8
            },
            "state": {
                "hover": {
                    "outerRadius": 0.85,
                    "stroke": '#000',
                    "lineWidth": 1
                },
                "selected": {
                    "outerRadius": 0.85,
                    "stroke": '#000',
                    "lineWidth": 1
                }
            }
        },
    })
    return data

history,today = process_checkgroup_efficiency_data()

variables = {
    "title": "分拣退换时效分布",
    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "table_1": build_chart_data("分拣退换时效分布(当月历史)",history.loc["4小时内","数量"],history.loc["4-8小时","数量"],history.loc["超8小时","数量"],
                                history.loc["4小时内","占比"],history.loc["4-8小时","占比"],history.loc["超8小时","占比"]),
    "y_4_rate":history.loc["4小时内","占比"],
    "y_4_8_rate":history.loc["4-8小时","占比"],
    "y_over8_rate":history.loc["超8小时","占比"],
    "count4":history.loc["4小时内","数量"],
    "count4_8":history.loc["4-8小时","数量"],
    "count_over8":history.loc["超8小时","数量"],
    "count4_today":today.loc["4小时内","数量"],
    "count48_today":today.loc["4-8小时","数量"],
    "count_over8_today":today.loc["超8小时","数量"],
    "y_4_rate_today":today.loc["4小时内","占比"],
    "y_4_8_rate_today":today.loc["4-8小时","占比"],
    "y_over8_rate_today":today.loc["超8小时","占比"],
    "table_2":build_chart_data("分拣退换时效分布(当日)",today.loc["4小时内","数量"],today.loc["4-8小时","数量"],today.loc["超8小时","数量"],
                                today.loc["4小时内","占比"],today.loc["4-8小时","占比"],today.loc["超8小时","占比"])
}

# 生成消息
# payload = build_message(
#     template_id="AAqBc0EeBjtyz",
#     template_version="1.0.10",
#     template_vars=variables
# )
#
#
# bot = AsBot("人机")
# bot.send_card_to_group(payload)


