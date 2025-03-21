from playwright.sync_api import sync_playwright
browser_path = "D:\Program Files\GptChrome\GptBrowser.exe"
def run():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(executable_path=browser_path, headless=False)
        page = browser.new_page()


        # 导航到目标页面
        page.goto('https://ddinter2.scbdd.com/server/inter-detail/204/')  # 替换为你的目标页面 URL

        # 循环点击按钮，直到按钮变为禁用状态
        while True:
            try:
                # 定位按钮
                button_selector = 'a.paginate_button.next'
                button = page.query_selector(button_selector)

                if not button:
                    print("未找到按钮，停止点击")
                    break

                # 检查按钮是否被禁用
                is_disabled = button.get_attribute('aria-disabled') == 'true' or 'disabled' in (button.get_attribute('class') or '')
                if is_disabled:
                    print("按钮已禁用，停止点击")
                    break

                # 点击按钮
                button.click()
                print("点击按钮")

                # 等待页面加载完成
                page.wait_for_load_state('networkidle')  # 等待网络空闲状态
            except Exception as e:
                print(f"发生错误: {e}")
                break

        # 关闭浏览器
        browser.close()

if __name__ == '__main__':
    run()