from bs4 import BeautifulSoup
from openai import OpenAI

class BilingualMarkdownScraper:
    def __init__(self, 
                 api_key: str,
                 base_url: str,
                 image_prefix: str = "",
                 chrome_driver_path: str = "chromedriver"):
        """
        :param api_key: OpenAI API key
        :param base_url: OpenAI API base url
        :param image_prefix: 图片前缀（如'https://www.electronics-tutorials.ws/'）
        :param chrome_driver_path: chromedriver的路径
        """
        self.api_key = api_key
        self.base_url = base_url
        self.image_prefix = image_prefix
        self.chrome_driver_path = chrome_driver_path
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def clean_html(self, html: str) -> str:
        """清洗HTML，只保留主要内容与图片"""
        soup = BeautifulSoup(html, "html.parser")
        headBox = soup.find(class_="head-box clearfix")
        content = soup.find(class_="content-cont")
        if headBox and content:
            return str(headBox) + str(content)
        else:
            body = soup.body
            return str(body) if body else html

    def html_to_markdown(self, html: str) -> str:
        """调用API让模型把HTML转成图片保留的Markdown（支持图片前缀）"""
        prompt = (
            html +
            f"\n\nBased on the content above, generate a markdown file. I only need the content inside — no extra commentary or additions. Keep all images, and ensure their prefix is `{self.image_prefix}`. Return the content directly in markdown format.\n"
            f"\n\n将上述html转成直接的 Markdown 格式，而不是保留 HTML 标签，保留所有原始内容，我只需要文件中的内容——不需要额外的评论或补充。保留所有图片，并确保它们的前缀为`{self.image_prefix}`，直接以 markdown 格式返回内容。\n"
        )
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4.1-nano",
        )
        return chat_completion.choices[0].message.content

    def bilingual_translate_markdown(self, markdown: str) -> str:
        """调用API让模型对Markdown做对照翻译（中英文交错）"""
        prompt = (
            markdown +
            "\nPlease break down the above content into multiple sentences for comparison translation, with each English sentence followed immediately by its Chinese translation. All titles and subheadings should also be translated, with the Chinese translation of each title and subheading immediately following the original English one, ensuring that the format of the Chinese titles and subheadings matches the original English format. The translation should retain the original Markdown format. All images and content should be kept, with only one formula and calculation expression retained, and only one image should be kept and returned directly."
        )
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
        )
        return chat_completion.choices[0].message.content
