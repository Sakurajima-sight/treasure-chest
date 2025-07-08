import asyncio
from crawl4ai import *
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd

BASE_URL = "https://www.electronics-tutorials.ws"

def convert_table_to_base64_image(table_tag):
    # 提取表格数据
    rows = []
    for row in table_tag.find_all("tr"):
        cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
        if cols:
            rows.append(cols)

    if not rows:
        return ""  # 空表格

    # 构建 DataFrame
    if len(rows) > 1:
        df = pd.DataFrame(rows[1:], columns=rows[0])
    else:
        df = pd.DataFrame(rows)

    # 渲染为图片
    fig, ax = plt.subplots(figsize=(len(df.columns)*2, len(df)*0.6))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
    table.scale(1, 1.5)

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    base64_img = base64.b64encode(buffer.read()).decode("utf-8")
    return f'<img src="data:image/png;base64,{base64_img}"/>'

def is_relative(url):
    return not url.startswith(("http://", "https://", "//"))

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.electronics-tutorials.ws/accircuits/ac-waveform.html",
        )
        html_content = result.html
        soup = BeautifulSoup(html_content, "html.parser")

        # 提取目标部分
        head_box = soup.find(class_="head-box clearfix")
        content_cont = soup.find(class_="content-cont")

        # 拼接为新的结构化 HTML
        new_soup = BeautifulSoup("", "html.parser")
        if head_box:
            new_soup.append(head_box)
        if content_cont:
            new_soup.append(content_cont)

        # 删除 class 同时包含 'clearfix' 和 'content-nav'，或单独包含 'social_box_buttons'
        for tag in new_soup.find_all(class_=lambda c: c and ("clearfix" in c and "content-nav" in c or "social_box_buttons" in c)):
            tag.decompose()

        # 补全 href 和 src 链接
        for tag in new_soup.find_all(["a", "img"]):
            if tag.name == "a" and tag.has_attr("href"):
                if is_relative(tag["href"]):
                    tag["href"] = urljoin(BASE_URL, tag["href"])
            if tag.name == "img" and tag.has_attr("src"):
                if is_relative(tag["src"]):
                    tag["src"] = urljoin(BASE_URL, tag["src"])

        # 转换 class="table1" 的表格为 base64 图片
        for table in new_soup.find_all("table", class_="table1"):
            img_tag = BeautifulSoup(convert_table_to_base64_image(table), "html.parser")
            table.replace_with(img_tag)

        # 美化输出
        pretty_html = new_soup.prettify()

        # 保存
        with open("1.AC Waveform and AC Circuit Theory.html", "w", encoding="utf-8") as f:
            f.write(pretty_html)

        print("✅ 已保存结构化、清洗、链接补全、表格图像化的 HTML 文件")

if __name__ == "__main__":
    asyncio.run(main())
