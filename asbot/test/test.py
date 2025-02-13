import time
from playwright.sync_api import sync_playwright


def send_bi_data():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto('http://127.0.0.1:1888/')
        page.locator('#userName').fill('laifen')
        page.locator('#passwd').fill('laifen666')
        page.locator('#login').click()
        time.sleep(2)

        page.locator('#sidebar_close').click()
        print('正在截图分拣')
        page.screenshot(path="../../data/image/picking.png", full_page=True)
        print('分拣截图成功')
        page.reload()
        time.sleep(2)
        page.locator('#userName').fill('laifen')
        page.locator('#passwd').fill('laifen666')
        page.locator('#login').click()
        time.sleep(2)
        page.locator('#tab-item2').click()
        time.sleep(1)
        page.locator('#sidebar_close').click()
        time.sleep(2)
        print('正在截图寄修')
        page.screenshot(path="../../data/image/send_fixing.png", full_page=True)
        print('寄修截图成功')
        print("截图已保存")

        browser.close()




send_bi_data()