from playwright.sync_api import sync_playwright

def capture_full_page(url, output_path="full_page_screenshot.png"):
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)  # headless=True 表示无头模式
        page = browser.new_page()

        # 打开网页
        page.goto(url)

        # 截取整个页面并保存为文件
        page.screenshot(path=output_path, full_page=True)
        print(f"截图已保存到: {output_path}")

        # 关闭浏览器
        browser.close()

# 调用函数截取网页
capture_full_page("http://localhost:999/superset/dashboard/11/?native_filters_key=757Bv25ON00CV6lBb7YtjkvLawb__hhtK5rJACcs9BlhAGbEwoVevvo4VfbSmAho", "example_full_page.png")
