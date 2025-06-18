import argparse
from bs4 import BeautifulSoup

def format_html(input_file, output_file):
    # 读取原始 HTML
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # 解析和格式化
    soup = BeautifulSoup(html, 'html.parser')
    pretty_html = soup.prettify()  # 这是关键，自动缩进和格式化

    # 保存为新 HTML 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_html)

    print(f"格式化后的HTML已保存为 {output_file}")

if __name__ == '__main__':
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='格式化 HTML 文件')
    parser.add_argument('-i', '--input', required=True, help='输入的 HTML 文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出的 HTML 文件路径')

    # 解析命令行参数
    args = parser.parse_args()

    # 调用格式化函数
    format_html(args.input, args.output)
