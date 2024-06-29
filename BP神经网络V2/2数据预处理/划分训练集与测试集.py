import pandas as pd  # 引入数据框
from sklearn.model_selection import train_test_split  # 用来划分训练集与测试集


def _data_cleaning(df):
    # 清除原网页中未记载数据
    for i in range(3,32):
        df = df.drop(index=df[df.iloc[:,i] == '--'].index)
    # 去除指标不需要列
    df = df.drop('成长能力指标', axis=1)
    df = df.drop('每股指标', axis=1)
    df = df.drop('盈利能力指标', axis=1)
    df = df.drop('运营能力指标', axis=1)
    df = df.drop('偿债能力指标', axis=1)
    df = df.drop('净利润(元)', axis=1)
    df = df.drop('扣非净利润(元)', axis=1)
    df = df.drop('营业总收入(元)', axis=1)
    # 百分数转化为浮点数
    df['净利润同比增长率'] = df['净利润同比增长率'].str.rstrip('%').astype('float') / 100.0
    df['扣非净利润同比增长率'] = df['扣非净利润同比增长率'].str.rstrip('%').astype('float') / 100.0
    df['营业总收入同比增长率'] = df['营业总收入同比增长率'].str.rstrip('%').astype('float') / 100.0
    df['销售净利率'] = df['销售净利率'].str.rstrip('%').astype('float') / 100.0
    df['销售毛利率'] = df['销售毛利率'].str.rstrip('%').astype('float') / 100.0
    df['净资产收益率'] = df['净资产收益率'].str.rstrip('%').astype('float') / 100.0
    df['净资产收益率-摊薄'] = df['净资产收益率-摊薄'].str.rstrip('%').astype('float') / 100.0
    df['资产负债率'] = df['资产负债率'].str.rstrip('%').astype('float') / 100.0
    # 货币单位转化为浮点数，因量纲差距过大此类数据删除
    # df['净利润(元)'] = df['净利润(元)'].apply(lambda x: float(x.replace('万', ''))
    #                                   * 10000 if '万' in x else float(x.replace('亿', '')) * 100000000)
    # df['扣非净利润(元)'] = df['扣非净利润(元)'].apply(lambda x: float(x.replace('万', ''))
    #                                       * 10000 if '万' in x else float(x.replace('亿', '')) * 100000000)
    # df['营业总收入(元)'] = df['营业总收入(元)'].apply(lambda x: float(x.replace('万', ''))
    #                                       * 10000 if '万' in x else float(x.replace('亿', '')) * 100000000)
    # 货币计数转化为浮点数
    df['基本每股收益(元)'] = df['基本每股收益(元)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['每股净资产(元)'] = df['每股净资产(元)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['每股资本公积金(元)'] = df['每股资本公积金(元)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['每股未分配利润(元)'] = df['每股未分配利润(元)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['每股经营现金流(元)'] = df['每股经营现金流(元)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['营业周期(天)'] = df['营业周期(天)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['存货周转率(次)'] = df['存货周转率(次)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['存货周转天数(天)'] = df['存货周转天数(天)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['应收账款周转天数(天)'] = df['应收账款周转天数(天)'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['流动比率'] = df['流动比率'].apply(lambda df: float(
        df.replace('$', '').replace(',', '')))
    df['速动比率'] = df['速动比率'].apply(lambda df: float(
        df.replace('$', '').replace(',', '')))
    df['保守速动比率'] = df['保守速动比率'].apply(
        lambda df: float(df.replace('$', '').replace(',', '')))
    df['产权比率'] = df['产权比率'].apply(lambda df: float(
        df.replace('$', '').replace(',', '')))
    return df




# 读取文件
df = pd.read_csv('../1数据采集/调试.csv',encoding='gbk')
df = df.dropna()  # 去除空白值
df = _data_cleaning(df)  # 去除未记载数据和转换格式

# 将尔康制药（违规）和中国医药（未违规）单独提出来作为预测集来测试泛化性能，泛化精度越高，模型实战效果越好
df_pr_1 = df[df['股票']=='尔康制药']  
df_pr_1 = pd.concat([df_pr_1[df_pr_1['时间'].str.contains('2015')],  # 选取违规年份
                   df_pr_1[df_pr_1['时间'].str.contains('2016')]])
df_pr_1['类别'] = 1
df_pr_0 = pd.concat(
    [
        df.query("股票=='中国医药' & 时间.str.contains('2015')"),
        df.query("股票=='中国医药' & 时间.str.contains('2016')"),
    ]
)
df_pr_0['类别'] = 0
df_pr = pd.concat([df_pr_1,df_pr_0],axis=0)
df_pr.to_csv('尔康&中国医药.csv',encoding='gbk')
# 删除尔康制药的留下来做训练集与测试集
df_total = df.drop(index=df[df['股票'] == '尔康制药'].index).drop(index=df[df['股票'] == '中国医药'].index) 
# 找到违规的打上标签1
df_1 = pd.concat(
    [
        df_total.query("股票 == '复星医药' & 时间.str.contains('2018')"),
        df_total.query("股票 == 'ST康美' & 时间.str.contains('2016')"),
        df_total.query("股票 == 'ST康美' & 时间.str.contains('2017')"),
        df_total.query("股票 == 'ST康美' & 时间.str.contains('2018')"),
        df_total.query("股票 == '思创医惠' & 时间.str.contains('2019')"),
        df_total.query("股票 == '思创医惠' & 时间.str.contains('2020')"),
        df_total.query("股票 == 'ST太安' & 时间.str.contains('2018')"),
        df_total.query("股票 == 'ST太安' & 时间.str.contains('2019')"),
        df_total.query("股票 == 'ST太安' & 时间.str.contains('2020')"),
        df_total.query("股票 == 'ST太安' & 时间.str.contains('2021')"),
        df_total.query("股票 == '亚太药业' & 时间.str.contains('2016')"),
        df_total.query("股票 == '亚太药业' & 时间.str.contains('2017')"),
        df_total.query("股票 == '亚太药业' & 时间.str.contains('2018')")
    ]
)
df_1['类别'] = 1
# 找到未违规的打上标签0
df_0 = df_total.drop(index=df[df['股票'] == '复星医药'].index)
df_0 = df_0.drop(index=df[df['股票'] == 'ST康美'].index)
df_0 = df_0.drop(index=df[df['股票'] == '思创医惠'].index)
df_0 = df_0.drop(index=df[df['股票'] == 'ST太安'].index)
df_0 = df_0.drop(index=df[df['股票'] == '亚太药业'].index)
df_0['类别'] = 0
# 合并数据集
df_total = pd.concat([df_1,df_0],axis=0)

# 划分训练集与测试集
X = df_total.iloc[:, 3:24]
y = df_total.iloc[:, 24:25]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
df_train = pd.concat([X_train, y_train],axis=1)
df_test = pd.concat([X_test, y_test],axis=1)
# 存储
df_train.to_csv('训练集.csv',encoding='gbk')
df_test.to_csv('测试集.csv',encoding='gbk')