import json
import plotly.graph_objects as go
import time
from datetime import datetime
import xlwings as xw
from PIL import ImageGrab
import logging

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='../log/app.log',  # 日志文件名
    filemode='a',  # 追加模式
    encoding='utf-8",',
)

# 创建一个控制台输出处理器
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console)  # 添加控制台处理器

# 读取 JSON 文件
def read_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 写入 JSON 文件
def write_config(file_path, config):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


def export_dataframe_to_image_v2(
    df,
    output_path,
    title="DataFrame Export",
    image_size=(800, 500),
    font_family="Arial",  # 确保兼容的字体
    font_size=18
):
    """
    将 pandas DataFrame 导出为图片，增强样式显示效果。

    参数：
    - df: pandas DataFrame，需要导出的数据
    - output_path: str，图片保存路径
    - title: str，图片标题
    - image_size: tuple，图片尺寸 (宽, 高)，默认 (800, 500)
    - font_family: str，字体样式，默认 "Arial"
    - font_size: int，字体大小，默认 18
    """
    # 配色方案
    header_color = [ "#007BFF", '#007BFF', '#007BFF', '#8081cf', '#8081cf', '#3cc08e', '#3cc08e']  # 表头背景色
    header_font_color = "white"  # 表头字体颜色
    cell_fill_colors = ["#F9F9F9", "#FFFFFF"]  # 单元格条纹背景
    cell_font_color = "#333333"  # 默认单元格字体颜色

    # 动态设置字体颜色：带 + 号的数字为红色
    font_colors = []
    for col in df.columns:
        col_colors = []
        for value in df[col]:
            if isinstance(value, str) and "+" in value:  # 判断是否包含 + 号
                col_colors.append("red")  # 红色
            # elif isinstance(value, str) and "-" in value: # 判断是否包含 - 号
            #     col_colors.append("00ff80")  # 绿色
            else:
                col_colors.append(cell_font_color)  # 默认颜色
        font_colors.append(col_colors)

    # 创建表格
    table = go.Figure(data=[go.Table(
        columnwidth=[1.5,1, 1.2, 1, 1.2, 1, 1.2],  # 列宽设置
        header=dict(
            values=[f"<b>{col}</b>" for col in df.columns],
            fill_color=header_color,
            align="center",
            font=dict(family=font_family, size=font_size, color=header_font_color),
            line_color="white",  # 表头边框颜色
            height=40  # 增大表头高度
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[cell_fill_colors * (len(df) // 2 + 1)],
            align="center",
            font=dict(family=font_family, size=font_size - 2),
            line_color="#E5E5E5",  # 单元格边框颜色
            height=30,  # 增大单元格高度
            font_color=font_colors  # 动态设置字体颜色
        )
    )])

    # 布局设置
    table.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=font_family, size=font_size + 4, color="#007BFF"),
            x=0.5,
            xanchor="center"
        ),
        margin=dict(l=20, r=20, t=70, b=20),  # 边距优化
        paper_bgcolor="white",  # 背景色
        width=image_size[0],
        height=image_size[1]
    )

    # 保存图片
    table.write_image(output_path, width=image_size[0], height=image_size[1], scale=3)
    logger.info(f"图片已保存到: {output_path}")

def export_dataframe_to_image_for_normal(
    df, 
    output_path, 
    title="DataFrame Export", 
    image_size=(800, 560), 
    font_family="Arial",  # 确保兼容的字体
    font_size=18
):
    """
    将 pandas DataFrame 导出为图片，增强样式显示效果。

    参数：
    - df: pandas DataFrame，需要导出的数据
    - output_path: str，图片保存路径
    - title: str，图片标题
    - image_size: tuple，图片尺寸 (宽, 高)，默认 (800, 560)
    - font_family: str，字体样式，默认 "Arial"
    - font_size: int，字体大小，默认 18
    """
    # 配色方案
    header_color = ['#007BFF', "#007BFF", '#007BFF', '#007BFF', '#8081cf', '#8081cf', '#3cc08e', '#3cc08e']  # 表头背景色
    header_font_color = "white"  # 表头字体颜色
    cell_fill_colors = ["#F9F9F9", "#FFFFFF"]  # 单元格条纹背景
    cell_font_color = "#333333"  # 默认单元格字体颜色
    font_colors = [cell_font_color] * len(df.columns)  # 字体颜色
    # # 动态设置字体颜色：带 + 号的数字为红色
    # font_colors = []
    # for col in df.columns:
    #     col_colors = []
    #     for value in df[col]:
    #         if isinstance(value, str) and "+" in value:  # 判断是否包含 + 号
    #             col_colors.append("red")  # 红色
    #         else:
    #             col_colors.append(cell_font_color)  # 默认颜色
    #     font_colors.append(col_colors)
    
    # 创建表格
    table = go.Figure(data=[go.Table(
        columnwidth=[2, 1.5, 1, 1.2, 1, 1.2, 1, 1.2],  # 列宽设置
        header=dict(
            values=[f"<b>{col}</b>" for col in df.columns],
            fill_color=header_color,
            align="center",
            font=dict(family=font_family, size=font_size, color=header_font_color),
            line_color="white",  # 表头边框颜色
            height=40  # 增大表头高度
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[cell_fill_colors * (len(df) // 2 + 1)],
            align="center",
            font=dict(family=font_family, size=font_size - 2),
            line_color="#E5E5E5",  # 单元格边框颜色
            height=30,  # 增大单元格高度
            font_color=font_colors  # 动态设置字体颜色
        )
    )])

    # 布局设置
    table.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=font_family, size=font_size + 4, color="#007BFF"),
            x=0.5,
            xanchor="center"
        ),
        margin=dict(l=20, r=20, t=70, b=20),  # 边距优化
        paper_bgcolor="white",  # 背景色
        width=image_size[0], 
        height=image_size[1]
    )

    # 保存图片
    table.write_image(output_path, width=image_size[0], height=image_size[1], scale=3)
    logger.info(f"图片已保存到: {output_path}")

def makeimage(quanlity, path):
    # 打开 Excel 文件
    app = xw.App(visible=False, add_book=True)
    app.display_alerts = False  # 关闭一些提示信息，可以加快运行速度。 默认为 True。
    app.screen_updating = True
    wb = app.books[0]
    worksheet = wb.sheets['Sheet1']

    worksheet.range('A:A').column_width = 20  # 设置 A 列的宽度为 20
    worksheet.range('B:B').column_width = 20  # 设置 B 列的宽度为 30
    worksheet.range('C:C').column_width = 30
    worksheet.range('D:D').column_width = 20
    worksheet.range('1:16').row_height = 24  # 设置 A 列的宽度为 20
    worksheet.api.Cells.Font.Name = '微软雅黑'  # 设置字体为 Arial
    worksheet.api.Cells.Font.Size = 15  # 设置字体大小为 12
    worksheet.api.Cells.Font.Bold = True  # 设置字体为粗体
    worksheet.api.Cells.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter  # 水平居中对齐
    worksheet.api.Cells.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter  # 垂直居中对齐
    columns_name = ['状态', '总计', datetime.now(), '数量', ]
    worksheet.range('A1').value = columns_name
    status = ['待发货', '待质检', '待维修-维修中', '待维修-已一检', '待维修-已分拣', '待分拣-已签收', '异常', ]

    for i in range(0, len(quanlity)):
        worksheet.range(f'D{i + 2}').value = quanlity[i]

    i = 2
    for statu in status:
        worksheet.range(f'C{i}:C{i + 1}').options(transpose=True).value = ['电吹风', '电动牙刷']
        dwx = worksheet.range(f'A{i}:A{i + 1}')
        total = worksheet.range(f'B{i}:B{i + 1}')
        total.api.Merge()
        dwx.api.Merge()
        dwx.value = statu
        i = i + 2

    worksheet.range('B2').formula = '=SUM(D2:D3)'
    worksheet.range('B2:B15').api.FillDown()

    worksheet.range('2:2').api.Insert()  # 在第 2 行之前插入一行
    worksheet.range('A2').value = '总计'
    worksheet.range('B2').formula = '=SUM(D3:D16)'
    worksheet.range('B2:D2').api.Merge()
    worksheet.range('B2').font.color = '#FF0000'
    worksheet.range('A1:D1').color = '#00CCFF'

    # 截图
    rng = worksheet.range('A1:D16')
    rng.api.CopyPicture(Appearance=1, Format=2)  # 改进 CopyPicture 调用
    time.sleep(2)  # 延迟时间适当增加

    rng = worksheet.range('A1:D16')

    # 使用 list comprehension 来遍历每个单元格并清理内容
    for cell in rng:
        if cell.value:
            # 移除所有空格和回车符
            cleaned_value = ''.join(str(cell.value).split())
            cell.value = cleaned_value

    # 获取剪贴板图片
    img = ImageGrab.grabclipboard()

    if img is not None:
        img.save(path)  # 保存图片至本地
        logger.info(f"图片保存成功！保存至{path}")

    else:
        logger.info("截图失败，剪贴板内容为空。")

    # 退出 Excel
    wb.close()
