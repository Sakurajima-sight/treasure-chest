import argparse
from bs4 import BeautifulSoup

def process_html(input_filename, output_filename, group_size, injected_text):
    # 1. 打开并读取 HTML 文件
    with open(input_filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # 2. 用 BeautifulSoup 解析
    soup = BeautifulSoup(html, 'html.parser')

    # 3. 找到所有 class 为 'head-box clearfix' 或 'content-cont' 的 div 元素作为一级
    parents = soup.find_all('div', class_=['head-box clearfix', 'content-cont'])

    # 创建一个文件来保存打印的内容
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        if not parents:
            output_file.write("<p>没有找到任何 head-box clearfix 或 content-cont 元素</p>")
            print("没有找到任何 head-box clearfix 或 content-cont 元素")
        else:
            # 收集所有的二级元素
            all_children = []
            for parent in parents:
                children = parent.find_all(recursive=False)
                all_children.extend(children)

            # 按每group_size个一组写入
            for i in range(0, len(all_children), group_size):
                group = all_children[i:i+group_size]
                output_file.write(f"第 {i//group_size + 1} 组内容\n")
                for idx, child in enumerate(group, 1):
                    output_file.write(child.prettify())

                # 注入内容，并加一个空行
                if injected_text:
                    output_file.write(f"{injected_text}\n\n")

    print(f"处理后的打印内容已保存为 {output_filename}")


if __name__ == "__main__":
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="处理 HTML 文件并按组保存输出内容")
    parser.add_argument("input_filename", help="输入的 HTML 文件路径")
    parser.add_argument("output_filename", help="输出的文件路径")
    parser.add_argument("group_size", type=int, help="每组写入的数量")
    parser.add_argument("--injected_text", help="每组内容后面注入的文本", default="")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用处理函数
    process_html(args.input_filename, args.output_filename, args.group_size, args.injected_text)
