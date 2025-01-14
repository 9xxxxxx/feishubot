from playwright.sync_api import sync_playwright

# 使用 Playwright 截图
with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 打开网页
    url = "http://172.16.102.217:8888/"
    page.goto(url)

    # 截图并保存
    output_file = "example_playwright.png"
    page.screenshot(path=output_file, full_page=True)

    # 关闭浏览器
    browser.close()

print(f"网页快照已保存为 {output_file}")
