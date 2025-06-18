import os
import json
import asyncio
from crawl4ai import *
from bs4 import BeautifulSoup  # 引入BeautifulSoup用于解析HTML
from typing import List


class Article:
    title: str
    link: str

    def __init__(self, title: str, link: str) -> None:
        self.title = title
        self.link = link


class UpdatedTopicsAndLinksValue:
    topic_url: str
    articles: List[Article]

    def __init__(self, topic_url: str, articles: List[Article]) -> None:
        self.topic_url = topic_url
        self.articles = articles


# 从当前文件夹加载 JSON 数据
def load_json_data(file_name: str):
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)


# 创建目录
def create_directories(topic_name):
    base_dir = "electronics-tutorials"
    topic_dir = os.path.join(base_dir, topic_name)
    os.makedirs(topic_dir, exist_ok=True)
    return topic_dir


# 处理src链接，补充网络前缀
def fix_image_src(src: str) -> str:
    if src and not src.startswith('http') and not src.startswith('https'):
        return f"https://www.electronics-tutorials.ws{src}"
    return src


# 爬取并保存特定部分内容
async def scrape_and_save_content(article: Article, folder_path: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=article.link)
        
        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(result.html, "html.parser")
        
        # 删除class="clearfix content-nav" 的部分
        content_nav = soup.find(class_="clearfix content-nav")
        if content_nav:
            content_nav.decompose()  # 删除该元素及其内容
        
        # 获取包含 class="head-box clearfix" 和 class="section row" 的部分
        head_box_content = soup.find(class_="head-box clearfix")
        section_row_content = soup.find(class_="section row")
        
        # 处理图片的src属性
        if head_box_content:
            # 查找所有的img标签，修正它们的src
            for img in head_box_content.find_all('img'):
                img['src'] = fix_image_src(img.get('src'))
        
        if section_row_content:
            # 查找所有的img标签，修正它们的src
            for img in section_row_content.find_all('img'):
                img['src'] = fix_image_src(img.get('src'))
        
        # 提取内容并合并
        content = ""
        if head_box_content:
            content += str(head_box_content)
        if section_row_content:
            content += str(section_row_content)
        
        # 使用prettify格式化HTML内容
        prettified_content = BeautifulSoup(content, "html.parser").prettify()

        # 保存提取的内容
        file_path = os.path.join(folder_path, f"{article.title}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(prettified_content)
        print(f"已保存 '{article.title}' 的特定内容到 {file_path}")


# 主函数，处理爬取并保存
async def main():
    # 从文件加载 JSON 数据
    data = load_json_data('updated_topics_and_links.json')
    
    for topic_name, topic_data in data.items():
        print(f"正在处理主题: {topic_name}")
        
        # 创建主题目录
        topic_folder = create_directories(topic_name)
        
        # 处理每个文章
        for article_data in topic_data["articles"]:
            article = Article(title=article_data["title"], link=article_data["link"])
            await scrape_and_save_content(article, topic_folder)


# 执行爬取和保存
if __name__ == "__main__":
    asyncio.run(main())
