# 导入所需的库
import os
from arrow import get
from playwright.sync_api import sync_playwright,expect
from datetime import datetime,timedelta

def get_datetime_conditions():
    now = datetime.now()

    # 计算昨天日期
    yesterday = now - timedelta(days=1)

    # 获取昨天开始时间（00:00:00）
    start_of_day = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取昨天结束时间（23:59:59）
    end_of_day = yesterday.replace(hour=23, minute=59, second=59, microsecond=0)

    # 格式化为字符串
    start_str = start_of_day.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_of_day.strftime('%Y-%m-%d %H:%M:%S')
    
    return start_str,end_str


def get_data(title,filename):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto('https://qingniao.1yangai.com/')
        # 登录
        page.locator('#login_username').fill('东莞市徕芬电子科技有限公司:黎金兰')
        page.locator('#login_password').fill('0255')
        page.get_by_role('button').click()
        
        
        # 点击工单列表
        page.locator('#root > div > aside > div.pro-layout-menu-area > ol > li:nth-child(4) > div > a > span').click()
        
        
        # 选择案例 
        # page.locator('#root > div > aside > div.pro-layout-menu-area > ol > li:nth-child(4) > div > a > span').click()
        # page.locator(f'//span[@class="antd-pro-pages-search-index-itemText" and text()="{title}"]').click()
        if title == '案例':
            page.locator('//*[@id="root"]/div/main/section/div/main/section/section[1]/div[1]/div/div/div[3]/span[1]').click()
            
        else:
            page.locator('//*[@id="root"]/div/main/section/div/main/section/section[1]/div[1]/div/div/div[5]/span[1]').click()
            
        page.wait_for_timeout(1500)
        
        
        # 清空条件，输入时间
        page.locator('//a[@class and normalize-space()="清空"]').click()
        start_str,end_str = get_datetime_conditions()
        
        page.locator('#create_time').click()
        page.locator('#create_time').clear()    
        page.locator('#create_time').fill(start_str)
        page.wait_for_timeout(1000)
        page.keyboard.press('Enter')

        page.locator('//*[@id="field_create_time"]/div/div/div[2]/div/div/div/div[3]/input').click()
        page.locator('//*[@id="field_create_time"]/div/div/div[2]/div/div/div/div[3]/input').clear()
        page.locator('//*[@id="field_create_time"]/div/div/div[2]/div/div/div/div[3]/input').fill(end_str)
        page.wait_for_timeout(1000)
        page.keyboard.press('Enter')
        
        
        
        page.wait_for_timeout(1000)
        # 检索数据并等待加载
        page.locator('//*[@id="root"]/div/main/section/div/main/section/section[1]/div[2]/div/section/section/div/button[1]/span').click()
        page.wait_for_timeout(3500)
        
        # 点击导出
        page.locator('//*[@id="root"]/div/main/section/div/header/div/div/div[3]/button/span').click()
        
        # 点击确定
        page.locator("//button[@class='ant-btn ant-btn-primary']/span[text()='确 定']/..").click()
        
        # 点击任务中心
        page.locator('#root > div > main > header > div.pro-layout-main-header-fixed-right > div > div.antd-pro-components-task-center-index-wrapper').click()

        
        
        download_base_dir = "E://Downloads//test_data"
        os.makedirs(download_base_dir, exist_ok=True)
        

        page.wait_for_timeout(12000)

        download_button = page.locator('tr:nth-child(odd) >> td:nth-child(6) >> text="下载"').first
        
        with page.expect_download() as download_info:
            download_button.click()
            download = download_info.value
            download.save_as(os.path.join(download_base_dir,filename))
            print(f'文件已保存到{os.path.join(download_base_dir,filename)}')
        
        page.wait_for_timeout(3000)
        context.close()
        browser.close()


if __name__ == '__main__':
    # titles = {'案例':f'案例-{datetime.today().strftime('%Y-%m-%d %H-%M')}.xlsx','问卷':f'问卷-{datetime.today().strftime('%Y-%m-%d %H-%M')}.xlsx'}
    # for key,value in titles.items():
    #     get_data(key,value)
    get_data('问卷','dd.xlsx')


