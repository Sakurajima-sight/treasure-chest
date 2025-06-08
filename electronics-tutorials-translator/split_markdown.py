import argparse
import re

def split_markdown_by_headers(filepath, num_per_section, output_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 获取所有标题行的下标
    header_indices = [i for i, line in enumerate(lines) if re.match(r'^#{1,6} ', line)]
    header_indices.append(len(lines))  # 加上结尾索引

    sections = []
    for i in range(0, len(header_indices) - 1, num_per_section):
        start = header_indices[i]
        end = header_indices[i + num_per_section] if i + num_per_section < len(header_indices) else len(lines)
        section = ''.join(lines[start:end])
        sections.append(section)

    with open(output_path, 'w', encoding='utf-8') as out:
        for idx, sec in enumerate(sections, 1):
            out.write(f"\n这是第 {idx} 部分\n\n")
            out.write(sec)

    print(f"已将分组内容写入 {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="按标题分组拆分 Markdown 文件")
    parser.add_argument('-i', '--input', type=str, required=True, help="输入 Markdown 文件路径")
    parser.add_argument('-n', '--num', type=int, required=True, help="每几标题为一组")
    parser.add_argument('-o', '--output', type=str, required=True, help="输出文件路径")
    args = parser.parse_args()

    split_markdown_by_headers(args.input, args.num, args.output)
