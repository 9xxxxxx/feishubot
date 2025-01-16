from src.my_utility import logger
import pandas as pd
import os

def data_wait4check_and_detect(path):
    _,extension = os.path.splitext(path)
    df = None
    if extension == '.csv':
        df = pd.read_csv(path)
    elif extension == '.xlsx':
        df = pd.read_excel(path)
    else:
        logger.info('文件类型错误,只接受csv或者xlsx文件')
        return
    
    df = df.query("申请类别!= '寄修/返修' and 处理状态!='已取消' and 检测结果 != '异常'")

    df['状态'] = '-'

    df.loc[df['旧件处理状态']=='已签收','状态'] = '待分拣'
    df.loc[df['旧件处理状态']=='已检测','状态'] = '待一检'
     
    df = df.query("状态 != '-'")

    df = df.pivot_table(index=['状态','产品类型'],values='单号',aggfunc='count')
    df = df.reset_index()
    
    df0 = df.query("状态 == '待一检'").copy()
    new_row0 = pd.DataFrame({'状态':'总计','产品类型':'-','单号':df0['单号'].sum()},index=[0])
    df0 = pd.concat([df0,new_row0],ignore_index=True)
    df0 = df0.sort_values('单号',ascending=False)
    
    df1 = df.query("状态 == '待分拣'").copy()
    new_row1= pd.DataFrame({'状态':'总计','产品类型':'-','单号':df1['单号'].sum()},index=[0])
    df1 = pd.concat([df1,new_row1],ignore_index=True)
    df1 = df1.sort_values('单号',ascending=False)
    
    df = pd.concat([df0,df1],ignore_index=True)
    df = df.rename(columns={'单号':'数量'})
    return df
