import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageGrab, ImageTk
import pytesseract
from difflib import SequenceMatcher
import threading

# 设置tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 根据实际情况修改路径

def ocr_from_image(image):
    """ 从图片中提取文本 """
    text = pytesseract.image_to_string(image, lang='chi_sim')  # 根据实际需求选择语言
    return text

def load_questions(file_path):
    """ 加载题库 """
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = [line.strip() for line in file]
    return questions

def similarity(a, b):
    """ 计算两个字符串的相似度 """
    return SequenceMatcher(None, a, b).ratio()

# def find_similar_lines(ocr_text, questions, threshold=0.3):
#     """ 找出相似度超过阈值的行 """
#     similar_lines = []
#     for question in questions:
#         if similarity(ocr_text, question) > threshold:
#             similar_lines.append(question)
#     return similar_lines
def find_similar_lines(ocr_text, questions, threshold=0.25):
    """ 找出相似度超过阈值的行及其后面的四行内容 """
    similar_lines = []
    for i, question in enumerate(questions):
        if similarity(ocr_text, question) > threshold:
            similar_lines.append(question)
            # 打印该行后面的四行内容
            for j in range(1, 6):
                if i + j < len(questions):
                    similar_lines.append(questions[i + j])
    return similar_lines


def capture_and_ocr():
    """ 捕获屏幕区域并进行OCR识别 """
    # 获取画布的尺寸
    canvas_width = 1000
    canvas_height = 600

    print("{"+str(root.winfo_rootx())+","+str(root.winfo_rooty())+"}")

    # 计算截图的新区域：从画布右侧开始，宽度与画布相同
    # x1 = root.winfo_rootx() - canvas_width  # 起始X坐标
    # x2 = x1 + canvas_width  # 结束X坐标
    # y1 = root.winfo_rooty()   # 起始Y坐标
    # y2 = y1 + canvas_height  # 结束Y坐标
    x1 = 200
    x2 = x1 + canvas_width
    y1 = 400
    y2 = y1 + canvas_height
    print("["+str(x1)+","+str(x2)+"]["+str(y1)+","+str(y2)+"]")
    img = ImageGrab.grab().crop((x1, y1, x2, y2))

    # 将截取的图片显示在画布上
    photo = ImageTk.PhotoImage(img)
    canvas.create_image(canvas_width, 0, anchor=tk.NE, image=photo)  # 显示在画布右侧
    canvas.image = photo  # 保持引用，防止垃圾回收

    # 进行OCR识别
    ocr_text = ocr_from_image(img)

    # 更新文本框内容
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, f"-----OCR-----:\n {ocr_text}\n")

    # 加载题库
    questions = load_questions(questions_file)

    # 查找相似行
    similar_lines = find_similar_lines(ocr_text, questions)

    # 输出结果
    result_text.insert(tk.END, "\n=====相似的行有=====\n")
    for line in similar_lines:
        result_text.insert(tk.END, f"{line}\n")

    # 定时再次执行
    root.after(300, capture_and_ocr)


# 主程序
if __name__ == "__main__":
    # 初始化窗口
    root = tk.Tk()
    root.title("OCR识别与题库比对")
    root.geometry("1400x1080")  # 设置窗口大小
    
    # 创建画布
    canvas = tk.Canvas(root, width=1000, height=600, bg='white', highlightthickness=2, highlightbackground="blue")
    canvas.pack(pady=10)

    # 创建文本框
    result_text = tk.Text(root, height=100, width=100)
    result_text.pack(pady=10)

    # 题库文件路径
    questions_file = 'tiku.txt'

    # 启动定时任务
    root.after(1000, capture_and_ocr)

    # 运行主循环
    root.mainloop()
