import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from log import logger

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1200,800')
    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': r"E:\Works\售后Bot\data\input"}
    options.add_experimental_option('prefs', prefs)
    # 你可以选择设置更多的浏览器选项
    driver = webdriver.Chrome(options=options)
    logger.info("初始化浏览器~")
    return driver

def login(driver, username, password):
    driver.get("https://ap6.fscloud.com.cn/t/laifen")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))

    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'kc-login').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/div')))
    logger.info("登录成功")

def navigate_to_page_and_download_data(driver, filename,day):
    # 点击逆向管理
    logger.info("正在下载瑞云寄修积压源文件~")
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/div/div[1]').click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/ul/li[2]')))

    # 点击服务单产品明细
    driver.find_element(By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/ul/li[2]').click()

    time.sleep(3)
    # 点击自定义
    driver.find_element(By.XPATH, '//*[@id="tab-custom"]/span/span/button/span').click()
    time.sleep(2)
    # 点击模板
    driver.find_element(By.XPATH, '//div[@class="new_active" and @title="瑞云寄修积压"]/div').click()
    time.sleep(2)
    # 点击筛选
    driver.find_element(By.XPATH,
                        '//*[@id="__qiankun_microapp_wrapper_for_mainweb__"]/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div[2]/button[2]/span/span').click()
    time.sleep(2)
    # 设置旧件筛选天数
    # driver.find_element(By.CSS_SELECTOR,
    #                     '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-drawer__wrapper.rt-xpc-drawer.plat-advanced-filter > div > div > section > div.rt-list-filter.padding-size-bottom > div > div.rt-view-wrapper > form > div:nth-child(1) > div > div:nth-child(6) > div.el-form-item__content > div > div > input').send_keys(
    #     day)
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-drawer__wrapper.rt-xpc-drawer.plat-advanced-filter > div > div > section > div.rt-list-filter.padding-size-bottom > div > div.rt-view-wrapper > form > div:nth-child(1) > div > div:nth-child(6) > div.el-form-item__content > div > div > input').send_keys(
        day)
    # 点击确定
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-drawer__wrapper.rt-xpc-drawer.plat-advanced-filter > div > div > section > div.rt-list-filter.padding-size-bottom > div > div.filter-btns-container > div > div > button.rt-button.rt-button--primary.rt-button--medium.rt-button--normal').click()
    time.sleep(1)
    # 设置文件名
    # 点击导出全部
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div:nth-child(12) > div > div > div.rt-view-wrapper > div.rt-header.rt-xpc-sticky.is-sticky > div.rt-plat-list-header-wrapper > div.rt-list-header > div > div.header-btns > div > div > div > button:nth-child(2) > span > span').click()
    # 设置文件名称
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.rc-section.rt-section.plat-section > div.section-body.rc-section-body > form > div.excelExport-card-form > div.el-row.is-align-top > div > div > div.el-form-item__content > div > div.el-input.rt-xpc-input > input').clear()
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.rc-section.rt-section.plat-section > div.section-body.rc-section-body > form > div.excelExport-card-form > div.el-row.is-align-top > div > div > div.el-form-item__content > div > div.el-input.rt-xpc-input > input').send_keys(
        filename)
    time.sleep(1)
    # 点击确定
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.plat-dialog-footer-buttons.has-border > button.rt-button.rt-button--primary.rt-button--medium.rt-button--normal > span > span').click()

    try:
        # 等待最多 10 秒，直到包含类名 "el-message__content" 的 <p> 元素可见
        success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "p.el-message__content"))
        )
        # 检查元素的文本内容是否为“导出成功”
        if success_message.text.strip() == "导出成功":
            logger.info("检测到成功消息：导出成功")
        else:
            logger.info(f"消息内容不匹配，检测到的文本为: {success_message.text.strip()}")
    except Exception as e:
        logger.info("未检测到成功消息或超时:", str(e))

    time.sleep(12)
    driver.quit()
