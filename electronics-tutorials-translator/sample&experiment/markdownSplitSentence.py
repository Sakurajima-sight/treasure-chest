import ipdb.stdout
import spacy
import re

# 加载spaCy模型
nlp = spacy.load("en_core_web_sm")

# 读取Markdown文件
def read_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 按照标题和子标题拆分文本，支持多级标题
def split_text_by_headings(md_content):
    sections = []
    img_pattern = r'<p align="center"><img [^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*></p>'

    current_section = {"title": None, "content": "", "level": 0}
    header_content = ""  # 用于保存标题前的内容
       
    # 用于替换图片占位符
    image_counter = 0
    img_placeholders = {}  # 存储占位符与图片的对应关系

    # 按行处理
    for line in md_content.splitlines():
        # 处理图片标签 (支持普通图片和base64嵌入图片)
        img_match = re.match(img_pattern, line)

        if img_match:
            # 替换图片标签为占位符
            image_counter += 1
            img_placeholder = f"Image_Placeholder_{image_counter}"
            img_placeholders[img_placeholder] = img_match.group(0)
            current_section["content"] += img_placeholder + "\n"
            continue
        
        # 判断是否为标题（#号的数量表示标题的级别）
        match = re.match(r'^(#{1,6})\s*(.*)', line)

        if match:
            # 如果当前已有内容，保存上一节
            if current_section["title"]:
                sections.append(current_section)
            # 更新当前的section
            current_section = {"title": match.group(2).strip(), "content": "", "level": len(match.group(1))}
        else:
            current_section["content"] += line + "\n"

    # 加入最后一个section
    if current_section["title"]:
        sections.append(current_section)
    
    header_content += img_placeholders["Image_Placeholder_1"] + "\n"

    return header_content, sections, img_placeholders

# 处理内容，可以在这里添加更多处理逻辑
def process_content_with_spacy(content):
    doc = nlp(content)
    processed_content = []
    # 这里只是做了一个简单的文本处理，您可以在这里根据需求添加更多处理逻辑
    for sent in doc.sents:
        processed_content.append(sent.text)
    return "\n".join(processed_content)

# 保存处理后的内容为Markdown文件
def save_md_file(header_content, sections, output_path, img_placeholders):
    with open(output_path, 'w', encoding='utf-8') as file:
        # 先写入标题前的内容
        file.write(header_content)
        
        # 然后写入每个section的内容
        for section in sections:
            # 写入标题
            file.write('#' * section["level"] + ' ' + section["title"] + "\n\n")
            
            # 替换占位符为图片标签
            content_with_images = section["content"]
            for placeholder, img_tag in reversed(list(img_placeholders.items())):
                content_with_images = content_with_images.replace(placeholder, img_tag)
            
            # 写入替换后的内容
            file.write(content_with_images + "\n")

# 主流程
def main(input_file, output_file):
    # 读取文件
    md_content = read_md_file(input_file)
    
    # 拆分成标题和内容，保留标题前的内容
    header_content, sections, img_placeholders = split_text_by_headings(md_content)
    
    # 处理每个部分的内容
    for section in sections:
        section["content"] = process_content_with_spacy(section["content"])

    # 保存回新的Markdown文件
    save_md_file(header_content, sections, output_file, img_placeholders)
    print(f"处理后的内容已保存到 {output_file}")

# 运行脚本
input_file = '1.AC Waveform and AC Circuit Theory.md'  # 输入文件路径
output_file = '1.AC Waveform and AC Circuit Theory split sentence.md'  # 输出文件路径
main(input_file, output_file)
