from ebooklib import epub
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Preformatted

import json

# 1. 读取JSON数据
data = {
    "title": "2025年度报告",
    "sections": [
        {"header": "一、经济指标", "content": "GDP同比增长6.5%，消费市场稳步复苏..."},
        {"header": "二、科技创新", "content": "人工智能领域专利数量增长30%..."}
    ]
}

# 2. PDF配置参数
pdf_path = "output.pdf"
font_path = r"C:\Windows\Fonts\simfang.ttf"  # 仿宋字体文件路径
font_size = 22  # 字号14pt（≈18.67px）
line_spacing = 1.8  # 1.5倍行距
margin = 13 * mm  # 边距20px（转换为毫米）

# 3. 注册中文字体
pdfmetrics.registerFont(TTFont('SimFang', font_path))

# 4. 定义样式
styles = getSampleStyleSheet()
custom_style = ParagraphStyle(
    name='CustomStyle',
    parent=styles['Normal'],
    fontName='SimFang',
    fontSize=font_size,
    leading=font_size * line_spacing,  # 行距计算
    spaceBefore=6,  # 段前间距
    spaceAfter=6,    # 段后间距
    firstLineIndent=28  # 28pt（两汉字缩进）[2,4](@ref)

)

# 5. 构建PDF内容流
content = []
# 添加标题
title_style = ParagraphStyle(
    name='TitleStyle',
    parent=custom_style,
    fontSize=18,
    alignment=1  # 居中
)


# # 添加正文段落
# for section in data['sections']:
#     content.append(Paragraph(f"<b>{section['header']}</b>", custom_style))
#     content.append(Paragraph(section['content'], custom_style))
#     content.append(Spacer(1, 12))



def extract_epub_info(epub_path):
    book = epub.read_epub(epub_path)
    # 获取元数据
    book_title = book.get_metadata('DC', 'title')[0][0]
    print(f"书名：{book_title}\n")

    # 提取目录和内容
    toc = []  # 存储目录结构
    content_dict = {}  # 存储章节标题与内容
    for item in book.get_items():
        if item.get_type() == 9:
            # 解析HTML内容
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            # chapter_title = soup.find('h1', 'h2').text if soup.find('h1') else "未命名章节"
            
            h1_tag = soup.find('h1')
            h2_tag = soup.find('h2') if not h1_tag else None
            chapter_title = (
                h1_tag.text if h1_tag 
                else h2_tag.text if h2_tag 
                else "未命名章节"
            )
           
            toc.append(chapter_title)
            content_text = soup.get_text()

            content_text = content_text.replace("\n", "<br/>\u00A0\u00A0\u00A0\u00A0")
            content_dict[chapter_title] = content_text
    
    # 输出目录
    print("目录：")
    for idx, title in enumerate(toc, 1):
        print(f"{idx}. {title}")
    
    # 输出内容
    # print("\n内容示例：")

    content.append(Paragraph(book_title, title_style))
    content.append(Spacer(1, 12))

    for title, text in content_dict.items():
        print(f"## {title}\n{text}...")  # 截取前200字符
        content.append(Paragraph(f"<b>{title}</b>", custom_style))
        content.append(Paragraph(text, custom_style))
        content.append(Spacer(1, 12))
    
    # 6. 生成PDF文档
    pdf_path = epub_path.replace("epub","pdf")  
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A5,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    doc.build(content)

extract_epub_info(r"C:\baidunetdiskdownload\books\背叛 (豆豆) (Z-Library).epub")