import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

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
        # 等待表格元素加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        element = driver.find_element("css selector", "table")
        element.screenshot(output_path)
    finally:
        driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)

def html_table2img(input_html, output_img_dir, output_html):
    os.makedirs(output_img_dir, exist_ok=True)
    
    # 获取输入文件的名称，用作前缀
    input_file_name = os.path.splitext(os.path.basename(input_html))[0]
    
    with open(input_html, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    table_list = soup.find_all("table")
    img_paths = []
    output_html_dir = os.path.dirname(output_html) 
    
    # 使用线程池并行化处理每个表格
    with ThreadPoolExecutor() as executor:
        futures = []
        for idx, table in enumerate(table_list, 1):
            # 为每个表格生成新的图片名称，加入输入 HTML 文件名作为前缀
            img_name = f"{input_file_name}-{idx}.png"
            img_path = os.path.join(output_img_dir, img_name)
            
            # 异步执行截图
            futures.append(executor.submit(save_table_as_img, str(table), img_path))
        
        # 等待所有截图任务完成
        for future in futures:
            future.result()
    
    # 替换表格为图片标签
    for idx, table in enumerate(table_list, 1):
        img_name = f"{input_file_name}-{idx}.png"
        img_path = os.path.join(output_img_dir, img_name)
        
        # 获取相对路径并替换 "\\" 为 "/"
        rel_img_path = os.path.relpath(img_path, output_html_dir)
        rel_img_path = rel_img_path.replace("\\", "/")
        
        # 用图片替代表格
        img_tag = soup.new_tag("img", src=f"./{rel_img_path}")
        table.replace_with(img_tag)
    
    # 保存修改后的 HTML 文件
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
