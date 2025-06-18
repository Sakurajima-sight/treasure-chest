import asyncio
import json
from crawl4ai import *
from bs4 import BeautifulSoup
import re

# 从文件读取 topics_and_links 数据
def load_topics_and_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 提取页面上的文章标题和链接
async def extract_articles_from_url(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # 找到包含所有 <li> 元素的部分
        category_box = soup.find('div', class_='category box')
        articles = []
        
        if category_box:
            items = category_box.find_all('li')
            for item in items:
                link = item.find('a')
                if link:
                    title = link.get_text()
                    href = link.get('href')
                    # 使用正则表达式去除数字和点之间的空格
                    formatted_title = re.sub(r'(\d+)\. ', r'\1.', title)  # 处理数字和点之间的空格
                    articles.append({
                        "title": formatted_title,
                        "link": href
                    })
        return articles

# 更新 JSON 数据
async def update_json_data(input_file, output_file):
    # 从文件加载原始数据
    topics_and_links = load_topics_and_links(input_file)
    
    updated_data = {}

    for topic, data in topics_and_links.items():
        print(f"正在抓取: {topic}")
        articles = await extract_articles_from_url(data["topic_url"])

        # 添加新的字段 articles
        updated_data[topic] = {
            "topic_url": data["topic_url"],
            "articles": articles
        }
    
    # 保存到新的 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(updated_data, json_file, ensure_ascii=False, indent=4)
    print(f"更新完成，数据已保存到 '{output_file}'.")

if __name__ == "__main__":
    input_file = 'topics_and_links.json'  # 输入文件路径
    output_file = 'updated_topics_and_links.json'  # 输出文件路径

    asyncio.run(update_json_data(input_file, output_file))
