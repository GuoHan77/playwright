from playwright.sync_api import sync_playwright
import pandas as pd

def intercept_xhr(url, browser_path):
    # 用于存储抓取到的 JSON 数据中的 data 字段
    data_list = []
    num = []

    with sync_playwright() as p:
        # 启动Chromium实例
        browser = p.chromium.launch(executable_path=browser_path, headless=False)
        # 创建一个页面对象
        page = browser.new_page()

        def handle_response(response):
            if response.request.resource_type == "xhr" and "inter-list" in response.url:
                print("向URL发送请求:", response.url)
                try:
                    json_data = response.json()
                    print("json数据:", json_data)
                    # 提取 data 字段并添加到列表中
                    if 'data' in json_data:
                        data_list.extend(json_data['data'])
                        num.append(json_data["recordsTotal"])
                except Exception as e:
                    print("解析 JSON 失败:", e)

        # 注册响应事件处理器
        page.on("response", handle_response)

        print(f"正在访问url: {url}")
        # 访问目标URL，并等待网络空闲状态
        page.goto(url, wait_until="networkidle")

        # 模拟滚动操作，直到所有数据加载完成
        while len(data_list) < num[0]:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1)  # 等待1秒，确保数据加载

        # 模拟点击 "Next" 按钮，直到无法点击
        while True:
            # 尝试定位 "Next" 按钮
            next_button = page.query_selector("a.paginate_button.next")
            if not next_button:
                print("未找到 'Next' 按钮")
                break

            # 检查按钮是否可点击（通过检查是否包含 'disabled' 类）
            is_disabled = next_button.get_attribute("class")
            if "disabled" in is_disabled:
                print("'Next' 按钮不可点击，结束操作")
                break

            # 点击 "Next" 按钮
            print("点击 'Next' 按钮")
            next_button.click()
            page.wait_for_timeout(1)  # 等待1秒，确保数据加载

        # 关闭浏览器
        browser.close()

    # 将抓取到的 data 字段数据转换为 DataFrame
    if data_list:
        df = pd.DataFrame(data_list)
        print("转换后的 DataFrame:")
        print(df)
    else:
        print("未抓取到数据")

# URL和浏览器路径
for i in range(3, 10):
    url = "https://ddinter2.scbdd.com/server/inter-detail/" + str(i) + "/"
    browser_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    intercept_xhr(url, browser_path)
