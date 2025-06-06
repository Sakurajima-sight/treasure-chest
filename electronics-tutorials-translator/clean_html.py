from bs4 import BeautifulSoup

# 读取原始 HTML
with open('6.Signed_Binary_Numbers.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 解析和格式化
soup = BeautifulSoup(html, 'html.parser')
pretty_html = soup.prettify()  # 这是关键，自动缩进和格式化

# 保存为新 HTML 文件
with open('6.Signed_Binary_Numbers_formatted.html', 'w', encoding='utf-8') as f:
    f.write(pretty_html)

print("格式化后的HTML已保存为 6.Signed_Binary_Numbers_formatted.html")
