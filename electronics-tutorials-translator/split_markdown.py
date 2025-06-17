import argparse
import re

def split_markdown_by_headers(filepath, num_per_section, output_path, prompt):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 获取所有标题行的下标
    header_indices = [i for i, line in enumerate(lines) if re.match(r'^#{1,6} ', line)]
    header_indices.append(len(lines))  # 加上结尾索引

    # 收集第一个标题之前的所有内容
    first_section_start = 0
    if header_indices:
        first_section_start = header_indices[0]

    # 准备存储各个部分
    sections = []
    # 处理标题之间的部分
    for i in range(0, len(header_indices) - 1, num_per_section):
        if i == 0 and first_section_start > 0:
            # 对于 i == 0，先处理第一部分
            section = ''.join(lines[0:first_section_start])
            
            # 将后面的部分追加到该部分
            start = header_indices[i]
            end = header_indices[i + num_per_section] if i + num_per_section < len(header_indices) else len(lines)
            section += ''.join(lines[start:end])  # 追加这一部分内容
            
        else:
            start = header_indices[i]
            end = header_indices[i + num_per_section] if i + num_per_section < len(header_indices) else len(lines)
            section = ''.join(lines[start:end])
        # 将内容部分包裹在双引号中
        section = f'"{section.strip()}"'
        
        # 如果有提示词，将其添加到每一部分的末尾，不包裹提示词
        if prompt:
            section += f'\n{prompt}\n'  # 不加引号
        
        sections.append(section)

    with open(output_path, 'w', encoding='utf-8') as out:
        for idx, sec in enumerate(sections, 1):
            out.write(f"\n第 {idx} 组内容\n")
            out.write(sec)

    print(f"已将分组内容写入 {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="按标题分组拆分 Markdown 文件，并可在每部分后插入提示词")
    parser.add_argument('-i', '--input', type=str, required=True, help="输入 Markdown 文件路径")
    parser.add_argument('-n', '--num', type=int, required=True, help="每几标题为一组")
    parser.add_argument('-o', '--output', type=str, required=True, help="输出文件路径")
    parser.add_argument('--prompt', type=str, default="", help="每部分后面要注入的提示词（可选）")
    args = parser.parse_args()

    split_markdown_by_headers(args.input, args.num, args.output, args.prompt)
