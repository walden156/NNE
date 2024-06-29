import pandas as pd  # 使用数据框进行数据读取与存储
from selenium import webdriver  # 导入selenium库进行爬虫
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Keys
import time  # 使用time库来实现暂停，减少爬虫过程中的报错
'''
因爬取数据量大请保障网络环境良好
'''


def _little_booton_click(_len_of_times, wd):  # 实现自动点击小按钮浏览不同时间
    global _call_times
    _click_times = 0
    while _click_times < 6 and _click_times < _len_of_times-6*(_call_times+1):
        wd.find_element(
            By.XPATH, '//div[@class="data-icon data-icon-next "]').click()
        time.sleep(0.2)
        _click_times += 1
    _call_times += 1


# 设置数据格式
dic = {
    '行业': [],
    '股票': [],
    '指标': [],
    '时间': [],
    '值': []
}
# 实例化webdriver对象，用来模拟浏览器操作
# option = webdriver.ChromeOptions()
# option.add_argument('--headless')
wd = webdriver.Chrome(
    service=Service(r'chromedriver.exe')
    # ,options=option  # 隐藏浏览器
)  # 务必使用版本为120开头的chrome浏览器!!!!，或者重新下载对应版本chromedriver.exe
wd.implicitly_wait(20)  # 隐式等待，防止网速问题造成报错
wd.get('https://stockpage.10jqka.com.cn/600518/finance/')
mainWindow = wd.current_window_handle  # 设置为操作窗口
# 读取文件
filename = '数据采集需求.xlsx'
df_nor = pd.read_excel(filename, '未舞弊').loc[:, ['证券名称', '所属行业']]
df_wrong = pd.read_excel(filename, '舞弊').loc[:, ['证券名称', '所属行业']]
df_all = pd.concat([df_nor, df_wrong], axis=0)
# 整理数据
lis_name = list(df_all.loc[:, '证券名称'])
lis_indus = list(df_all.loc[:, '所属行业'])
# 进入子HTML页面
wd.switch_to.frame('dataifm')
lis_item = wd.find_elements(
    By.XPATH, '//div[@class="left_thead"]/table[@class="tbody"]/tbody/*')
lis_item = [i.text for i in lis_item]
# 回到主HTML页面
wd.switch_to.default_content()

# 开始爬取
for _loc in range(0, len(lis_name)):  # 按照公司名称一个一个爬取
    # '''调试'''
    # if _loc == 99:
    #     break
    time.sleep(0.5)
    # 找到输入框
    input = wd.find_element(By.XPATH, '//input[@id="search_input"]')
    input.send_keys(Keys.BACK_SPACE)  # 删除输入框原有内容，执行多次确保删干净
    input.send_keys(Keys.BACK_SPACE)
    input.send_keys(Keys.BACK_SPACE)
    input.send_keys(Keys.BACK_SPACE)
    input.send_keys(Keys.BACK_SPACE)
    input.send_keys(lis_name[_loc])  # 输入股票名称
    input.send_keys(Keys.BACKSPACE)  # 删除一个字来规避反爬虫
    input.send_keys(Keys.CONTROL, 'z')  # 撤回删除防止有相似名称股票
    time.sleep(2)  # 等待网站js反应
    input.send_keys(Keys.ENTER)  # 回车
    # 转移到新页面
    try:  # 如果股票已经退市，则直接进入下一个循环
        wd.switch_to.window(wd.window_handles[1])
    except:
        continue
    # 点击财务分析
    wd.find_element(
        By.XPATH, './/a[@stat="f10_sp_finance"]').click()
    wd.switch_to.window(wd.window_handles[1])
    # 进入子HTML页面
    wd.switch_to.frame('dataifm')
    # 流程化爬取
    _name_of_industry = lis_indus[_loc]  # 获取所爬股票行业信息
    _name_of_stock = lis_name[_loc]  # 获取所爬名称行业信息
    _date_line_of_this_stock = wd.find_elements(
        # 获取所爬股票的信息时间轴
        By.XPATH, '//table[@class="top_thead" and @style="width: 100%;"]//tr/*')
    _len_of_times = len(wd.find_elements(
        # 时间轴总长度
        By.XPATH, '//table[@class="top_thead" and @style="width: 100%;"]/tbody/tr/*'))
    _count = 1  # 翻小页次数
    _call_times = 0  # 调用翻小页函数的次数
    for i in range(0, _len_of_times // 6 + 1):  # 在总长度中分6个6个爬取
        # '''
        # 调试
        # '''
        # if _count == 7:
        #     break
        # 三元表达式，表明这次翻页后需要录入多少列
        _needed_times = 6 if 6 * _count < _len_of_times else _len_of_times % 6
        _value_tb = wd.find_elements(
            # 网站的数据表格
            By.XPATH, '//table[@class="tbody" and @style="top: 0px; width: 100%;"]/tbody/*')
        for height in range(0, 29):  # 长
            _name_of_item = lis_item[height]  # 第height行的指标名称
            _value = _value_tb[height]  # 第height行的时间序列数据
            _value = _value.find_elements(By.XPATH, './*')  # 抓取一整行
            for times in range(0, _needed_times):  # 宽
                dic['行业'].append(_name_of_industry)  # 遍历一整行的所有指标值，并推入字典对应列表
                dic['股票'].append(_name_of_stock)
                dic['指标'].append(_name_of_item)
                dic['时间'].append(_date_line_of_this_stock[times+6*i].text)
                dic['值'].append(_value[times+6*i].text)
        _count += 1
        _little_booton_click(_len_of_times, wd)  # 点击数据表的翻页按钮
    wd.close()  # 爬取完毕，关闭这只股票的页面
    wd.switch_to.window(wd.window_handles[0])  # 回到上一个窗口

df = pd.DataFrame(dic)  # 保存为数据框
df = df.drop_duplicates()  # 去除重复的样本
df1 = df.pivot(index=['行业', '股票', '时间'], columns='指标',
               values='值')  # 转换格式，重新设定索引
df1.to_csv('数据采集结果.csv', encoding='gbk')  # 保存为文件
