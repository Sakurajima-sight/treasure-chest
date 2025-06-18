import asyncio
import json
from crawl4ai import *
from bs4 import BeautifulSoup

async def main():
    # 使用 AsyncWebCrawler 爬取指定网页
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.electronics-tutorials.ws/",
        )
        
        # 获取爬取的 html 内容
        html_content = result.html
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 创建一个字典来存储每个主题的名称和链接
        topics = {}

        # 定义网站的前缀
        base_url_prefix = "https://www.electronics-tutorials.ws/"

        # 查找所有 class 为 top-categories 的 div 元素
        top_categories_elements = soup.find_all(class_="top-categories")
        
        for category in top_categories_elements:
            clearfix_elements = category.find_all(class_="clearfix")
            
            # 遍历找到的 clearfix 元素，提取其中的 href 链接
            for clearfix in clearfix_elements:
                links = clearfix.find_all('a', href=True)  # 提取所有包含 href 属性的 <a> 标签
                for link in links:
                    href = link['href']

                    # 只保留以指定前缀开头的链接
                    if href.startswith(base_url_prefix):

                        # 查找 h2 标签中的内容作为 topic_name
                        h2_tag = link.find('h2')
                        if h2_tag:
                            topic_name = h2_tag.get_text().strip()
                        else:
                            # 如果没有 h2 标签，使用链接的文本作为主题名称
                            topic_name = link.get_text().strip()

                        # 将主题名称和链接存入字典
                        topics[topic_name] = {
                            'topic_url': href,
                        }
                        
        # 将数据保存为 JSON 格式
        with open("topics_and_links.json", "w", encoding="utf-8") as file:
            json.dump(topics, file, ensure_ascii=False, indent=4)

        print("Topics and links have been saved to 'topics_and_links.json'.")

if __name__ == "__main__":
    asyncio.run(main())
