import os
import time
import asyncio
import threading
import http.server
import socketserver
from bs4 import BeautifulSoup, NavigableString
from dotenv import load_dotenv
from openai import OpenAI
from crawl4ai import AsyncWebCrawler
import re

# ==== 1. 环境变量加载 & 大模型接口 ====
load_dotenv()
API_KEY = os.getenv("QWEN3_API_KEY")
DEFAULT_MODEL = "qwen-max"

def ask_model(prompt_text, model=DEFAULT_MODEL, max_retries=3, retry_interval=2):
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ai.erikpsw.works",
    )
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.0,
                stream=True
            )
            full_reply_content = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_reply_content += chunk.choices[0].delta.content
            return full_reply_content.strip()
        except Exception as e:
            print(f"调用大模型失败，重试中：{e}")
        if attempt < max_retries:
            time.sleep(retry_interval)
    raise Exception(f"接口请求失败，已重试{max_retries}次仍未成功。")

# ==== 2. 处理 HTML、占位符替换 ====
file_path = "1.AC Waveform and AC Circuit Theory.html"
with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

def is_txt_class(tag):
    return tag.name == "span" and tag.get("class") and any('txt' in c for c in tag['class'])

formula_map = {}
img_map = {}

def process_node(parent):
    global formula_idx, img_idx
    i = 0
    children = list(parent.contents)
    while i < len(children):
        node = children[i]
        if isinstance(node, NavigableString):
            i += 1
            continue
        # 合并连续 txt 类 span
        if is_txt_class(node):
            group = [node]
            j = i + 1
            while j < len(children) and is_txt_class(children[j]):
                group.append(children[j])
                j += 1
            merged_html = "".join(str(x) for x in group)
            placeholder = f"__MARKDOWN_FORMULA_{formula_idx}__"
            formula_map[placeholder] = merged_html
            group[0].replace_with(placeholder)
            for t in group[1:]:
                t.extract()
            formula_idx += 1
            children = list(parent.contents)
            i = 0
            continue
        # img base64 占位
        elif getattr(node, 'name', None) == "img" and node.get("src", "").startswith("data:image"):
            placeholder = f"__MARKDOWN_IMG_{img_idx}__"
            img_map[placeholder] = str(node)
            node.replace_with(placeholder)
            img_idx += 1
            children = list(parent.contents)
            i = 0
            continue
        else:
            process_node(node)
        i += 1

formula_idx = 1
img_idx = 1

if soup.body:
    process_node(soup.body)
else:
    process_node(soup)

# 包装完整HTML
def wrap_html_body(content, title="Document"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
</head>
<body>
{content}
</body>
</html>"""

html_with_placeholders = str(soup)
html_full = wrap_html_body(html_with_placeholders, title="AC Waveform and AC Circuit Theory")
html_with_placeholders_path = "html_with_placeholders.html"
with open(html_with_placeholders_path, "w", encoding="utf-8") as f:
    f.write(html_full)

# ==== 3. 启动本地 HTTP 服务 ====
PORT = 8000

class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(html_with_placeholders_path)))
    with socketserver.TCPServer(("", PORT), SilentHTTPRequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}/")
        httpd.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1)  # 等待服务器启动

# ==== 4. Crawl4AI 本地抓取并转 Markdown ====
async def crawl_and_convert():
    url = f"http://localhost:{PORT}/{html_with_placeholders_path}"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

markdown = asyncio.run(crawl_and_convert())

# ==== 5. 占位符替换（公式：大模型，图片：嵌入 base64） ====
# 公式
for placeholder, tag_html in formula_map.items():
    prompt = f'"{tag_html}" 将该html转成markdown中的latex公式，全部用$包裹，若有"• "，直接去掉即可，直接返回转换后的结果，其他内容都不要返回。'
    latex = ask_model(prompt)
    markdown = markdown.replace(placeholder, latex)

# 图片：还原为base64 markdown图片
for placeholder, img_html in img_map.items():
    m = re.search(r'src="([^"]+)"', img_html)
    img_src = m.group(1) if m else ""
    markdown_img = f"![]({img_src})" if img_src else "![公式图片](#)"
    markdown = markdown.replace(placeholder, markdown_img)

def center_all_images(md_text):
    # 匹配 ![alt](url)（包括 base64 和普通图片）
    def repl(m):
        alt = m.group(1)
        url = m.group(2)
        return f'<p align="center"><img src="{url}" alt="{alt}"/></p>'
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', repl, md_text)

markdown = center_all_images(markdown)

# ==== 6. 保存结果，删除临时文件 ====
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

os.remove(html_with_placeholders_path)

print("转换完成，已保存为 output.md")
