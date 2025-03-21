from playwright.sync_api import sync_playwright
import pandas as pd
import os
import logging

# 配置日志
logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def intercept_xhr(url, browser_path, all_data):
    data_list = []
    num = []

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=browser_path, headless=False)
        page = browser.new_page()

        def handle_response(response):
            if response.request.resource_type == "xhr" and "inter-list" in response.url:
                print("向URL发送请求:", response.url)
                try:
                    json_data = response.json()
                    print("json数据:", json_data)
                    if 'data' in json_data:
                        data_list.extend(json_data['data'])
                        num.append(json_data["recordsTotal"])
                except Exception as e:
                    print("解析 JSON 失败:", e)

        page.on("response", handle_response)

        print(f"正在访问url: {url}")
        page.goto(url, wait_until="networkidle")

        while len(data_list) < num[0]:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            while True:
                try:
                    # 定位按钮
                    button_selector = 'a.paginate_button.next'

                    # 等待按钮加载
                    page.wait_for_selector(button_selector, state='attached', timeout=5000)
                    button = page.query_selector(button_selector)

                    if not button:
                        print("未找到按钮，停止点击")
                        break

                    # 检查按钮是否被禁用
                    is_disabled = button.get_attribute('aria-disabled') == 'true' or 'disabled' in (
                            button.get_attribute('class') or '')
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



        browser.close()

    if data_list:
        df = pd.DataFrame(data_list)
        print(f"当前页面抓取到的 DataFrame (URL: {url}):")
        print(df)
        all_data = pd.concat([all_data, df], ignore_index=True)
    else:
        print(f"未抓取到数据 (URL: {url})")

    return all_data

# 初始化一个空的 DataFrame 用于存储所有数据
all_data = pd.DataFrame()

# 检查是否存在临时文件，如果存在则加载
temp_file = "temp_data.csv"
if os.path.exists(temp_file):
    all_data = pd.read_csv(temp_file)
    print("加载临时文件中的数据，继续爬取...")

# 检查日志文件，加载已爬取的URL
log_file = 'crawler.log'
crawled_urls = set()
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            if "成功爬取URL" in line:
                url = line.split("成功爬取URL: ")[1].strip()
                crawled_urls.add(url)

# URL和浏览器路径
start_index = len(all_data) + 1  # 从上次中断的地方继续
for i in range(start_index, 8576 + 1):
    url = "https://ddinter2.scbdd.com/server/inter-detail/" + str(i) + "/"
    browser_path = "D:\Program Files\GptChrome\GptBrowser.exe"

    if url in crawled_urls:
        print(f"URL {url} 已经爬取过，跳过...")
        continue

    try:
        all_data = intercept_xhr(url, browser_path, all_data)
        # 每次爬取后保存临时文件
        all_data.to_csv(temp_file, index=False)
        print(f"已保存临时文件: {temp_file}")
        # 记录成功爬取的URL
        logging.info(f"成功爬取URL: {url}")
    except Exception as e:
        print(f"爬取过程中出现异常: {e}")
        logging.error(f"爬取URL {url} 时出现异常: {e}")
        break

# 保存总的 DataFrame 到 CSV 文件
if not all_data.empty:
    output_file = "all_data.csv"
    all_data.to_csv(output_file, index=False)
    print(f"所有数据已保存到 {output_file}")
    # 删除临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"已删除临时文件: {temp_file}")
else:
    print("未抓取到任何数据")