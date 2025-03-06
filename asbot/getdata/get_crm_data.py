import pandas as pd

# 获取crm手工创单量
def get_crm_data(path):
    df = pd.read_excel(path)
    df = df[['单号', '单据来源', '创建时间', '旧件签收时间']]
    df = df.rename(columns={'单据来源':'平台'})
    df['创建时间'] = pd.to_datetime(df['创建时间'], errors='coerce')
    df['旧件签收时间'] = pd.to_datetime(df['旧件签收时间'], errors='coerce')
    df['时间差'] = (df['旧件签收时间'] - df['创建时间']).dt.total_seconds() / (24 * 3600)
    df['日期'] = df["旧件签收时间"].dt.strftime("%Y-%m-%d")

    bf = df[df["时间差"] <= 1].copy()
    bf['数量'] = 1
    df_filled = bf.pivot_table(index='日期', columns='平台', values='数量', aggfunc='sum', fill_value=0)
    df_filled.reset_index(inplace=True)
    df_filled['日期'] = pd.to_datetime(df_filled['日期'])
    df_filled.set_index("日期", inplace=True)
    # 将日期列转换为中文格式的字符串
    df_filled.index = df_filled.index.strftime("%m月%d日")

    return df_filled



