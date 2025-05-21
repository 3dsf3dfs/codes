import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ebooklib import epub
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Preformatted
import time;
import json


# # 添加正文段落
# for section in data['sections']:
#     content.append(Paragraph(f"<b>{section['header']}</b>", custom_style))
#     content.append(Paragraph(section['content'], custom_style))
#     content.append(Spacer(1, 12))



def extract_epub_info(epub_path):

    # 2. PDF配置参数
    pdf_path = "output.pdf"
    font_path = r"C:\Windows\Fonts\simfang.ttf"  # 仿宋字体文件路径
    font_size = 20  # 字号14pt（≈18.67px）
    line_spacing = 1.6  # 1.5倍行距
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
        fontSize=23,
        alignment=1  # 居中
    )



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

            content_text = content_text.replace("\n", "<br/><br/>\u00A0\u00A0\u00A0\u00A0")
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
        # print(f"## {title}\n{text}...")  # 截取前200字符
        content.append(Paragraph(f"<b>{title}</b>", custom_style))
        content.append(Paragraph(text, custom_style))
        content.append(Spacer(1, 12))
    
    # 6. 生成PDF文档
    pdf_path = epub_path.replace(".epub","-puretext.pdf")  
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A5,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    doc.build(content)

# extract_epub_info(r"C:\baidunetdiskdownload\books\背叛 (豆豆) (Z-Library).epub")

class DragDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # 窗口基础设置
        self.setWindowTitle('多文件拖放工具')
        self.setGeometry(300, 300, 1000, 800)
        
        # 创建主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 设置垂直布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 拖放区域提示标签
        self.label = QLabel("拖放文件到此处（支持多选）", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                padding: 20px;
                font-size: 35px;
                color: #666;
            }
        """)
        layout.addWidget(self.label)
        
        # 启用拖放功能
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        # 验证拖入内容是否包含文件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  # 接受拖放操作
        else:
            event.ignore()

    def dropEvent(self, event):
        # 处理拖放的文件
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        
        # 循环输出绝对路径
        for index, path in enumerate(file_paths, 1):
            # print(f"文件{index}: {path}")

            start_time = time.time()
            print(path ,"start")
            extract_epub_info(path);
            end_time = time.time()
            print(path ,"ok" ,f"耗时: {end_time - start_time:.4f} 秒")
        
        # 更新界面提示
        self.label.setText(f"已接收 {len(file_paths)} 个文件\n路径已输出到控制台")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())