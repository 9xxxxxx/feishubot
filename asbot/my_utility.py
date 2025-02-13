import json
import time
from datetime import datetime
import xlwings as xw
from PIL import ImageGrab
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def generate_asd_wc_image(df, path, title):
    logger.info("开始生成售后业务量预计图")
    # 获取唯一的取件天数分类
    categories = df['取件天数'].unique().tolist()
    categories.sort()

    # 创建子图
    fig = make_subplots(
        rows=2,  # 两行布局
        cols=4,  # 四列布局
        row_heights=[0.8, 0.2],  # 第一行高度占 80%，第二行高度占 20%
        vertical_spacing=0.05,  # 减小行间距
        specs=[
            [{"type": "pie"}, {"type": "pie"}, {"type": "pie"}, {"type": "pie"}],  # 第一行是 4 个饼图
            [{"type": "domain", "colspan": 4}, None, None, None]  # 第二行用于文字，跨 4 列
        ],
        subplot_titles=[f"{category} (总数: {df[df['取件天数'] == category]['数量'].sum()})" for category in categories]
        # 子标题，显示总数
    )

    # 动态添加饼图
    for i, category in enumerate(categories, start=1):
        filtered_df = df.query(f"取件天数 == '{category}'")
        labels = filtered_df['地区'].tolist()
        values = filtered_df['数量'].tolist()

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                textinfo='label+value',
                textposition='inside',
                sort=True,
                rotation=180,  # 从正上方开始
                direction='clockwise'  # 顺时针排列
            ),
            row=1,
            col=i
        )

    # 添加文字说明
    text = """
    1. 华北地区：北京市、天津市、河北省、山西省、内蒙古自治区<br>
    2. 华东地区：上海市、江苏省、浙江省、安徽省、福建省、江西省、山东省、台湾省<br>
    3. 华中地区：河南省、湖北省、湖南省<br>
    4. 华南地区：广东省、广西壮族自治区、海南省、香港特别行政区、澳门特别行政区<br>
    5. 西南地区：重庆市、四川省、贵州省、云南省、西藏自治区<br>
    6. 西北地区：陕西省、甘肃省、青海省、宁夏回族自治区、新疆维吾尔自治区<br>
    7. 东北地区：辽宁省、吉林省、黑龙江省<br>
    """

    fig.add_annotation(
        x=0.5,  # 文字水平居中
        y=0.05,  # 文字垂直位置（靠近底部）
        text=text,  # 文字内容
        showarrow=False,  # 不显示箭头
        font=dict(size=12, color="black"),  # 字体样式
        xref="paper",  # 使用相对坐标
        yref="paper",  # 使用相对坐标
        align="left",  # 文字左对齐
        xanchor="center",  # 文字水平锚点居中
        yanchor="top"  # 文字垂直锚点顶部对齐
    )

    # 更新布局
    fig.update_layout(
        title_text=title,
        title_x=0.5,  # 主标题居中
        title_y=0.95,  # 调整主标题的垂直位置
        showlegend=True,
        width=1000,  # 增加宽度以容纳 4 个饼图
        height=500,  # 增加高度以容纳文字
        margin=dict(l=20, r=20, t=80, b=150),  # 增加底部边距以容纳文字
        title_font=dict(size=28)
    )

    # 调整子标题位置
    for annotation in fig.layout.annotations:
        if annotation.text.startswith(tuple(categories)):  # 饼图子标题
            annotation.update(y=0.15, font=dict(size=16))

    # 显示图表
    logger.info(f'图片生成成功，保存至{path}')
    # 保存图表
    fig.write_image(path, scale=3)


def make_crm_image(df_filled,iamge_path,title):
    # 创建子图对象（双 Y 轴）
    fig = make_subplots(specs=[[{"secondary_y": True}]])  # 启用右侧 Y 轴

    # 添加柱状图（晓多和聚水潭，使用右侧 Y 轴）
    fig.add_trace(go.Bar(
        x=df_filled.index,  # X 轴：日期（已转换为中文格式）
        y=df_filled["晓多"],  # Y 轴：晓多列数据
        name="晓多",  # 图例名称
        marker_color="blue",  # 柱状图颜色
        text=df_filled["晓多"],  # 数据标签
        textposition="outside"  # 数据标签位置
    ), secondary_y=True)  # 使用右侧 Y 轴

    fig.add_trace(go.Bar(
        x=df_filled.index,
        y=df_filled["聚水潭"],
        name="聚水潭",
        marker_color="green",
        text=df_filled["聚水潭"],  # 数据标签
        textposition="outside"  # 数据标签位置
    ), secondary_y=True)  # 使用右侧 Y 轴

    # 添加折线图（CRM，使用左侧 Y 轴）
    fig.add_trace(go.Scatter(
        x=df_filled.index,  # X 轴：日期（已转换为中文格式）
        y=df_filled["CRM"],  # Y 轴：CRM 列数据
        name="CRM",  # 图例名称
        mode="lines+markers+text",  # 折线 + 数据点 + 数据标签
        line=dict(color="red", width=2),  # 折线样式
        marker=dict(size=10),  # 数据点样式
        text=df_filled["CRM"],  # 数据标签
        textposition="top center"  # 数据标签位置
    ), secondary_y=False)  # 使用左侧 Y 轴

    # 设置左侧 Y 轴范围
    fig.update_yaxes(
        range=[0, 500],  # 设置左侧 Y 轴范围为 0 到 450
        secondary_y=False
    )

    # 设置右侧 Y 轴范围
    fig.update_yaxes(
        range=[0, 400],  # 设置右侧 Y 轴范围为 0 到 500
        secondary_y=True
    )

    # 更新布局
    fig.update_layout(
        title=title,  # 图表标题
        title_x=0.5,
        title_font=dict(size=28),
        xaxis_title="日期",  # X 轴标题
        yaxis_title="CRM 的数量",  # 左侧 Y 轴标题
        yaxis2_title="晓多和聚水潭的数量",  # 右侧 Y 轴标题
        barmode="group",  # 柱状图分组显示
        template="plotly_white",  # 主题样式
        height=500,
        width=1500,
    )

    # 设置 X 轴显示中文“月-日”格式
    fig.update_xaxes(
        tickangle=45,  # 旋转日期标签
        tickmode="auto",  # 自动调整刻度
        nticks=len(df_filled)  # 显示所有日期
    )

    # 显示图表
    fig.write_image(iamge_path, scale=3)


