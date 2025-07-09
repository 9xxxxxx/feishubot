from my_utility import logger
import pandas as pd


def extractinfo(path, outpath, showdate):
    # logger.info(f'正在处理-{path}')
    df = pd.read_excel(path)
    myrows = df.query(" 发货状态.isnull() or 发货状态 == '待安排发货' ")
    # myrows = df.query("发货时间.isnull()")
    rydf = myrows.query(" 申请类别 == '寄修/返修' ")
    data_0 = rydf.query("处理状态 != '已取消'")
    data = data_0.query("产品类型 == '产成品-电动牙刷' or 产品类型 == '产成品-吹风机'")

    # tobedeliver = data.query(" 质检完成时间.notnull() and 发货时间.isnull() and 旧件处理状态 == '已质检'")
    # 待发货
    tobedeliver = data.query(" 质检完成时间.notnull()")
    # 待维修
    tobefix = data.query("质检完成时间.isnull() and 维修完成时间.isnull()")
    # 待质检
    tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull()")
    # tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull() and 旧件处理状态 == '已维修'")


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
    logger.info(f"截止{showdate}，瑞云未发货共{dataall}台")
    logger.info(f'处理完成，文件保存至-{outpath}')
    return data_to_send


def extractinfo_last(last_time_file_path):
    # logger.info(f'正在处理-{path}')
    df = pd.read_excel(last_time_file_path)
    data_0 = df.query(" 发货状态.isnull() or 发货状态 == '待安排发货' ")
    data_0 = data_0.query(" 申请类别 == '寄修/返修' and 处理状态 != '已取消'")

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

def make_jx_data(path,outpath,showdate,last_path):
    latest_data = extractinfo(path, outpath, showdate)
    last_data = extractinfo_last(last_path)
    send_data = latest_data.copy()

    send_data['合计流转量'] = latest_data['合计'] - last_data['合计']
    send_data['牙刷流转量'] = latest_data['电动牙刷'] - last_data['电动牙刷']
    send_data['风机流转量'] = latest_data['电吹风'] - last_data['电吹风']

    send_data['合计流转量'] = send_data['合计流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    send_data['牙刷流转量'] = send_data['牙刷流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    send_data['风机流转量'] = send_data['风机流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    return send_data


if __name__ == '__main__':
    extractinfo(r"E:\Dev\AS_Bot\asbot\getdata\瑞云寄修积压_20250313.xlsx",'15deal.xlsx','最近15')