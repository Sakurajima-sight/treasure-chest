import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1200,800')
    return webdriver.Chrome(options=options)

def table_html_wrapper(table_html):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    table {{ border-collapse: collapse; font-size:14px; }}
    th, td {{ border: 1px solid #999; padding: 6px 12px; }}
</style>
</head>
<body>{table_html}</body>
</html>"""

def save_table_as_img(table_html, output_path):
    driver = setup_driver()
    temp_html = "temp_table_render.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(table_html_wrapper(table_html))
    try:
        driver.get("file://" + os.path.abspath(temp_html))
        time.sleep(0.6)
        element = driver.find_element("css selector", "table")
        element.screenshot(output_path)
    finally:
        driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)

def html_table2img(input_html, output_img_dir, output_html):
    os.makedirs(output_img_dir, exist_ok=True)
    with open(input_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    table_list = soup.find_all("table")
    img_paths = []
    prefix = os.path.splitext(os.path.basename(output_html))[0]
    for idx, table in enumerate(table_list, 1):
        img_name = f"{prefix}_table{idx}.png"
        img_path = os.path.join(output_img_dir, img_name)
        save_table_as_img(str(table), img_path)
        rel_img_path = os.path.relpath(img_path, os.path.dirname(output_html))
        img_tag = soup.new_tag("img", src=rel_img_path)
        table.replace_with(img_tag)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("用法: python html2img.py <输入html文件> <图片输出文件夹> <输出html文件>")
        sys.exit(1)
    input_html = sys.argv[1]
    output_img_dir = sys.argv[2]
    output_html = sys.argv[3]
    html_table2img(input_html, output_img_dir, output_html)
    print("处理完毕！")
