import time
from datetime import datetime
from log import logger
import pandas as pd
import xlwings as xw
from PIL import ImageGrab
import plotly.graph_objects as go


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

def extractinfo(path, outpath, showdate):
    # logger.info(f'正在处理-{path}')
    df = pd.read_excel(path)
    # myrows = df.query(" 发货状态.isnull() or 发货状态 == '待安排发货' ")
    myrows = df.query(" 发货时间.isnull()")
    rydf = myrows.query(" 申请类别 == '寄修/返修' ")
    data_0 = rydf.query("处理状态 != '已取消'")
    data = data_0.query("产品类型 == '产成品-电动牙刷' or 产品类型 == '产成品-吹风机'")

    # tobedeliver = data.query(" 质检完成时间.notnull() and 发货时间.isnull() and 旧件处理状态 == '已质检'")
    # 待发货
    tobedeliver = data.query(" 质检完成时间.notnull()")
    # 待维修
    tobefix = data.query("质检完成时间.isnull() and 维修完成时间.isnull()")
    # 待质检
    # tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull() and 旧件处理状态 == '已维修'")
    tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull()")

    in_maintenance = tobefix.query(" 旧件处理状态 == '维修中'")
    checked = tobefix.query("旧件处理状态 == '已检测' ")
    first_Detected = tobefix.query(" 旧件处理状态 == '已一检'")
    Signed = tobefix.query(" 旧件处理状态 == '已签收'")
    first_Detected_exception = tobefix.query("旧件处理状态 == '一检异常'")
    checked_exception = tobefix.query("旧件处理状态 == '异常'")
    Exception_all = data.query("检测结果 == '异常'")

    with pd.ExcelWriter(outpath, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='数据源', index=False)
        tobedeliver.to_excel(writer, sheet_name='待发货', index=False)
        tobeqc.to_excel(writer, sheet_name='待质检', index=False)

        tobefix.to_excel(writer, sheet_name='待维修', index=False)
        in_maintenance.to_excel(writer, sheet_name='待维修-维修中', index=False)
        first_Detected.to_excel(writer, sheet_name='待维修-已一检待派工', index=False)
        checked.to_excel(writer, sheet_name='待维修-已分拣待一检', index=False)
        Signed.to_excel(writer, sheet_name='待分拣-已签收待分拣', index=False)
        Exception_all.to_excel(writer, sheet_name='异常', index=False)

    dataall = data['单号'].shape[0]

    in_maintenance_all = in_maintenance['单号'].shape[0]
    first_Detected_all = first_Detected['单号'].shape[0]
    Signed_all = Signed['单号'].shape[0]
    checked_all = checked['单号'].shape[0]

    checked_exception_all = checked_exception['单号'].shape[0]
    first_Detected_exception_all = first_Detected_exception['单号'].shape[0]

    tobedeliver_dcf = tobedeliver.query('产品类型 == "产成品-吹风机"').shape[0]
    tobedeliver_ddys = tobedeliver.query('产品类型 == "产成品-电动牙刷"').shape[0]

    tobeqc_dcf = tobeqc.query('产品类型 == "产成品-吹风机"').shape[0]
    tobeqc_ddys = tobeqc.query('产品类型 == "产成品-电动牙刷"').shape[0]

    in_maintenance_dcf = in_maintenance.query('产品类型 == "产成品-吹风机"').shape[0]
    in_maintenance_ddys = in_maintenance.query('产品类型 == "产成品-电动牙刷"').shape[0]

    checked_dcf = checked.query('产品类型 == "产成品-吹风机"').shape[0]
    checked_ddys = checked.query('产品类型 == "产成品-电动牙刷"').shape[0]

    first_Detected_dcf = first_Detected.query('产品类型 == "产成品-吹风机"').shape[0]
    first_Detected_ddys = first_Detected.query('产品类型 == "产成品-电动牙刷"').shape[0]

    Signed_dcf = Signed.query('产品类型 == "产成品-吹风机"').shape[0]
    Signed_ddys = Signed.query('产品类型 == "产成品-电动牙刷"').shape[0]

    checked_exception_all_dcf = checked_exception.query('产品类型 == "产成品-吹风机"').shape[0]
    checked_exception_all_ddys = checked_exception.query('产品类型 == "产成品-电动牙刷"').shape[0]

    first_Detected_exception_all_dcf = first_Detected_exception.query('产品类型 == "产成品-吹风机"').shape[0]
    first_Detected_exception_all_ddys = first_Detected_exception.query('产品类型 == "产成品-电动牙刷"').shape[0]

    dcf_quantity = {
        '电吹风-待发货': tobedeliver_dcf,
        '电吹风-待质检': tobeqc_dcf,
        '电吹风-维修中': in_maintenance_dcf,
        '电吹风-待派工': tobeqc_dcf,
        '电吹风-待一检': checked_dcf,
        '电吹风-待分拣': tobeqc_dcf,
        '电吹风_分拣异常': checked_exception_all_dcf,
        '电吹风_一检异常': first_Detected_exception_all_dcf,

    }
    status = {'状态': ['待分拣-已签收',
                       '待维修-已分拣',
                       '待维修-已一检',
                       '待维修-维修中',
                       '待质检',
                       '待发货',
                       '分拣异常',
                       '一检异常',
                       ]}

    dcf = {'电吹风': [tobedeliver_dcf,
                      tobeqc_dcf,
                      in_maintenance_dcf,
                      tobeqc_dcf,
                      checked_dcf,
                      tobeqc_dcf,
                      checked_exception_all_dcf,
                      first_Detected_exception_all_dcf]}

    ddys = {'电动牙刷': [tobedeliver_ddys,
                         tobeqc_ddys,
                         in_maintenance_ddys,
                         tobeqc_ddys,
                         checked_ddys,
                         tobeqc_ddys,
                         checked_exception_all_ddys,
                         first_Detected_exception_all_ddys]}

    ddys_quantity = {
        '电动牙刷-待发货': tobedeliver_ddys,
        '电动牙刷-待质检': tobeqc_ddys,
        '电动牙刷-维修中': in_maintenance_ddys,
        '电动牙刷-待派工': first_Detected_ddys,
        '电动牙刷-待一检': checked_ddys,
        '电动牙刷-待分拣': Signed_ddys,
        '电动牙刷_分拣异常': checked_exception_all_ddys,
        '电动牙刷_一检异常': first_Detected_exception_all_ddys
    }
    data = {'状态': ['待分拣-已签收',
                     '待维修-已分拣',
                     '待维修-已一检',
                     '待维修-维修中',
                     '待质检',
                     '待发货',
                     '分拣异常',
                     '一检异常',
                     ],
            '电动牙刷': [
                Signed_ddys,
                checked_ddys,
                first_Detected_ddys,
                in_maintenance_ddys,
                tobeqc_ddys,
                tobedeliver_ddys,
                checked_exception_all_ddys,
                first_Detected_exception_all_ddys],

            '牙刷流转量': [0, 0, 0, 0, 0, 0, 0, 0],

            '电吹风': [
                Signed_dcf,
                checked_dcf,
                first_Detected_dcf,
                in_maintenance_dcf,
                tobeqc_dcf,
                tobedeliver_dcf,
                checked_exception_all_dcf,
                first_Detected_exception_all_dcf],
            '风机流转量': [0, 0, 0, 0, 0, 0, 0, 0],
            }
    message = f"截止{showdate}，瑞云未发货共{dataall}台\n" \
              f"待发货：{tobedeliver_dcf + tobedeliver_ddys}台(吹风机{tobedeliver_dcf}台，电动牙刷{tobedeliver_ddys}台)\n" \
              f"待质检：{tobeqc_dcf + tobeqc_ddys}台(吹风机{tobeqc_dcf}台、电动牙刷{tobeqc_ddys}台)\n" \
              f"待维修：{checked_all + first_Detected_all + in_maintenance_all} (吹风机{checked_dcf + first_Detected_dcf + in_maintenance_dcf}、电动牙刷{checked_ddys + first_Detected_ddys + in_maintenance_ddys})\n" \
              f"\t已一检-待派工：{first_Detected_all}台 (吹风机{first_Detected_dcf}台、电动牙刷{first_Detected_ddys}台)\n" \
              f"\t已分检-待一检：{checked_all}台 (吹风机{checked_dcf}台、电动牙刷{checked_ddys}台)\n" \
              f"\t维修中：{in_maintenance_all}台(吹风机{in_maintenance_dcf}台、电动牙刷{in_maintenance_ddys}台)\n" \
              f"已签收-待分拣：{Signed_all}台 (吹风机{Signed_dcf}台、电动牙刷{Signed_ddys}台)\n" \
              f"异常：{checked_exception_all + first_Detected_exception_all}台 (分拣异常{checked_exception_all}台、一检异常{first_Detected_exception_all}台)\n" \
              f"具体清单如下，请查收"

    data_to_send = pd.DataFrame(data)
    data_to_send['合计'] = data_to_send['电动牙刷'] + data_to_send['电吹风']
    data_to_send['合计流转量'] = data_to_send['牙刷流转量'] + data_to_send['风机流转量']
    new_row = pd.DataFrame(
        {'状态': '总计', '电动牙刷': data_to_send['电动牙刷'].sum(), '牙刷流转量': data_to_send['牙刷流转量'].sum(),
         '电吹风': data_to_send['电吹风'].sum(), '风机流转量': data_to_send['风机流转量'].sum(),
         '合计': data_to_send['合计'].sum(), '合计流转量': data_to_send['合计流转量'].sum()}, index=[0])
    data_to_send = pd.concat([data_to_send, new_row], ignore_index=True)

    new_order = ['状态', '合计', '合计流转量', '电动牙刷', '牙刷流转量', '电吹风', '风机流转量']
    data_to_send = data_to_send.reindex(columns=new_order)
    logger.info(message)
    logger.info(f'处理完成，文件保存至-{outpath}')
    return data_to_send

def extractinfo_last(last_time_file_path):
    # logger.info(f'正在处理-{path}')
    df = pd.read_excel(last_time_file_path)
    data_0 = df.query(" 发货时间.isnull() and 申请类别 == '寄修/返修' and 处理状态 != '已取消'")
    # rydf = myrows.query("  ")
    # data_0 = rydf.query("")

    data = data_0.query("产品类型 == '产成品-电动牙刷' or 产品类型 == '产成品-吹风机'")

    tobedeliver = data.query(" 质检完成时间.notnull() and 发货时间.isnull() and 旧件处理状态 == '已质检'")
    tobefix = data.query("质检完成时间.isnull() and 维修完成时间.isnull()")
    tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull() and 旧件处理状态 == '已维修'")

    in_maintenance = tobefix.query(" 旧件处理状态 == '维修中'")
    checked = tobefix.query("旧件处理状态 == '已检测' ")
    first_Detected = tobefix.query(" 旧件处理状态 == '已一检'")
    Signed = tobefix.query(" 旧件处理状态 == '已签收'")
    first_Detected_exception = tobefix.query("旧件处理状态 == '一检异常'")
    checked_exception = tobefix.query("旧件处理状态 == '异常'")

    dataall = data['单号'].shape[0]

    in_maintenance_all = in_maintenance['单号'].shape[0]
    first_Detected_all = first_Detected['单号'].shape[0]
    Signed_all = Signed['单号'].shape[0]
    checked_all = checked['单号'].shape[0]

    checked_exception_all = checked_exception['单号'].shape[0]
    first_Detected_exception_all = first_Detected_exception['单号'].shape[0]

    tobedeliver_dcf = tobedeliver.query('产品类型 == "产成品-吹风机"').shape[0]
    tobedeliver_ddys = tobedeliver.query('产品类型 == "产成品-电动牙刷"').shape[0]

    tobeqc_dcf = tobeqc.query('产品类型 == "产成品-吹风机"').shape[0]
    tobeqc_ddys = tobeqc.query('产品类型 == "产成品-电动牙刷"').shape[0]

    in_maintenance_dcf = in_maintenance.query('产品类型 == "产成品-吹风机"').shape[0]
    in_maintenance_ddys = in_maintenance.query('产品类型 == "产成品-电动牙刷"').shape[0]

    checked_dcf = checked.query('产品类型 == "产成品-吹风机"').shape[0]
    checked_ddys = checked.query('产品类型 == "产成品-电动牙刷"').shape[0]

    first_Detected_dcf = first_Detected.query('产品类型 == "产成品-吹风机"').shape[0]
    first_Detected_ddys = first_Detected.query('产品类型 == "产成品-电动牙刷"').shape[0]

    Signed_dcf = Signed.query('产品类型 == "产成品-吹风机"').shape[0]
    Signed_ddys = Signed.query('产品类型 == "产成品-电动牙刷"').shape[0]

    checked_exception_all_dcf = checked_exception.query('产品类型 == "产成品-吹风机"').shape[0]
    checked_exception_all_ddys = checked_exception.query('产品类型 == "产成品-电动牙刷"').shape[0]

    first_Detected_exception_all_dcf = first_Detected_exception.query('产品类型 == "产成品-吹风机"').shape[0]
    first_Detected_exception_all_ddys = first_Detected_exception.query('产品类型 == "产成品-电动牙刷"').shape[0]

    dcf_quantity = {
        '电吹风-待发货': tobedeliver_dcf,
        '电吹风-待质检': tobeqc_dcf,
        '电吹风-维修中': in_maintenance_dcf,
        '电吹风-待派工': tobeqc_dcf,
        '电吹风-待一检': checked_dcf,
        '电吹风-待分拣': tobeqc_dcf,
        '电吹风_分拣异常': checked_exception_all_dcf,
        '电吹风_一检异常': first_Detected_exception_all_dcf,

    }
    status = {'状态': ['待分拣-已签收',
                       '待维修-已分拣',
                       '待维修-已一检',
                       '待维修-维修中',
                       '待质检',
                       '待发货',
                       '分拣异常',
                       '一检异常',
                       ]}

    dcf = {'电吹风': [tobedeliver_dcf,
                      tobeqc_dcf,
                      in_maintenance_dcf,
                      tobeqc_dcf,
                      checked_dcf,
                      tobeqc_dcf,
                      checked_exception_all_dcf,
                      first_Detected_exception_all_dcf]}

    ddys = {'电动牙刷': [tobedeliver_ddys,
                         tobeqc_ddys,
                         in_maintenance_ddys,
                         tobeqc_ddys,
                         checked_ddys,
                         tobeqc_ddys,
                         checked_exception_all_ddys,
                         first_Detected_exception_all_ddys]}

    ddys_quantity = {
        '电动牙刷-待发货': tobedeliver_ddys,
        '电动牙刷-待质检': tobeqc_ddys,
        '电动牙刷-维修中': in_maintenance_ddys,
        '电动牙刷-待派工': first_Detected_ddys,
        '电动牙刷-待一检': checked_ddys,
        '电动牙刷-待分拣': Signed_ddys,
        '电动牙刷_分拣异常': checked_exception_all_ddys,
        '电动牙刷_一检异常': first_Detected_exception_all_ddys
    }
    data = {'状态': ['待分拣-已签收',
                     '待维修-已分拣',
                     '待维修-已一检',
                     '待维修-维修中',
                     '待质检',
                     '待发货',
                     '分拣异常',
                     '一检异常',
                     ],
            '电动牙刷': [
                Signed_ddys,
                checked_ddys,
                first_Detected_ddys,
                in_maintenance_ddys,
                tobeqc_ddys,
                tobedeliver_ddys,
                checked_exception_all_ddys,
                first_Detected_exception_all_ddys],

            '牙刷流转量': [0, 0, 0, 0, 0, 0, 0, 0],

            '电吹风': [
                Signed_dcf,
                checked_dcf,
                first_Detected_dcf,
                in_maintenance_dcf,
                tobeqc_dcf,
                tobedeliver_dcf,
                checked_exception_all_dcf,
                first_Detected_exception_all_dcf],
            '风机流转量': [0, 0, 0, 0, 0, 0, 0, 0],
            }
    # message = f"截止{showdate}，瑞云未发货共{dataall}台\n" \
    #           f"待发货：{tobedeliver_dcf + tobedeliver_ddys}台(吹风机{tobedeliver_dcf}台，电动牙刷{tobedeliver_ddys}台)\n" \
    #           f"待质检：{tobeqc_dcf + tobeqc_ddys}台(吹风机{tobeqc_dcf}台、电动牙刷{tobeqc_ddys}台)\n" \
    #           f"待维修：{checked_all + first_Detected_all + in_maintenance_all} (吹风机{checked_dcf + first_Detected_dcf + in_maintenance_dcf}、电动牙刷{checked_ddys + first_Detected_ddys + in_maintenance_ddys})\n" \
    #           f"\t已一检-待派工：{first_Detected_all}台 (吹风机{first_Detected_dcf}台、电动牙刷{first_Detected_ddys}台)\n" \
    #           f"\t已分检-待一检：{checked_all}台 (吹风机{checked_dcf}台、电动牙刷{checked_ddys}台)\n" \
    #           f"\t维修中：{in_maintenance_all}台(吹风机{in_maintenance_dcf}台、电动牙刷{in_maintenance_ddys}台)\n" \
    #           f"已签收-待分拣：{Signed_all}台 (吹风机{Signed_dcf}台、电动牙刷{Signed_ddys}台)\n" \
    #           f"异常：{checked_exception_all + first_Detected_exception_all}台 (分拣异常{checked_exception_all}台、一检异常{first_Detected_exception_all}台)\n" \
    #           f"具体清单如下，请查收"

    # logger.info(message)
    # logger.info(f'处理完成，文件保存至-{outpath}')

    data_to_send = pd.DataFrame(data)
    data_to_send['合计'] = data_to_send['电动牙刷'] + data_to_send['电吹风']
    data_to_send['合计流转量'] = data_to_send['牙刷流转量'] + data_to_send['风机流转量']
    new_row = pd.DataFrame(
        {'状态': '总计', '电动牙刷': data_to_send['电动牙刷'].sum(), '牙刷流转量': data_to_send['牙刷流转量'].sum(),
         '电吹风': data_to_send['电吹风'].sum(), '风机流转量': data_to_send['风机流转量'].sum(),
         '合计': data_to_send['合计'].sum(), '合计流转量': data_to_send['合计流转量'].sum()}, index=[0])
    data_to_send = pd.concat([data_to_send, new_row], ignore_index=True)

    new_order = ['状态', '合计', '合计流转量', '电动牙刷', '牙刷流转量', '电吹风', '风机流转量']
    data_to_send = data_to_send.reindex(columns=new_order)
    # print(message)
    # print(f'处理完成，文件保存至-{outpath}')

    return data_to_send

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
    print(f"图片已保存到: {output_path}")
 
