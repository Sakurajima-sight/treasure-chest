import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

def html_to_image(html_str, output_file='output.png'):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=800,600')
    driver = webdriver.Chrome(options=options)

    # 包裹基础HTML与样式，防止样式丢失
    html_content = f"""{html_str}"""

    temp_file = 'temp_render.html'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    try:
        driver.get("file://" + os.path.abspath(temp_file))
        time.sleep(0.6)  # 等待渲染
        try:
            element = driver.find_element("css selector", ".table2")
            element.screenshot(output_file)
        except Exception:
            driver.save_screenshot(output_file)
        print(f"已保存图片: {output_file}")
    finally:
        driver.quit()
        if os.path.exists(temp_file):
            os.remove(temp_file)
            # print("临时文件已删除")

if __name__ == '__main__':
    print("请粘贴HTML片段（多行支持），完毕后按 Ctrl+D（Linux/Mac）或 Ctrl+Z 回车（Windows）：")
    html_code = sys.stdin.read()
    # 支持命令行参数自定义输出路径
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    html_to_image(html_code.strip(), output_file)
