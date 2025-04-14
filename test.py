# import re
# from docx import Document
#
# def extract_requirements_Vni(document_content):
#     """Phân tích và trích xuất yêu cầu từ nội dung tài liệu"""
#     if not document_content:
#         return []
#
#     # Danh sách các pattern phát hiện yêu cầu
#     patterns = [
#         r'^(Yêu cầu\s*(chức năng|phi chức năng)?\s*[\d.]*:*)\s*(.*)',  # Các loại yêu cầu
#         r'^(FR|NFR)\d*\s*[:-]\s*(.*)',  # FR/NFR
#         r'^\d+\.\d+\.?\d*\s*-\s*(.*)',  # Định dạng số thứ tự
#         r'^\s*[\*\-\+]?\s*(Yêu cầu.*|hệ thống.*|phải có.*|khả năng.*|phải.*|cần.*|người dùng.*|khi.*)',
#         # Bullet points với từ khóa
#         r'^\s*\*\s*(.*?)\s*\*',  # Văn bản trong dấu sao
#     ]
#
#     requirements = []
#     lines = document_content.split('\n')
#
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
#
#         for pattern in patterns:
#             match = re.match(pattern, line, re.IGNORECASE)
#             if match:
#                 groups = match.groups()
#                 requirement = groups[-1].strip()
#                 if requirement:
#                     requirements.append(requirement)
#                 break  # Chỉ cần khớp với 1 pattern
#
#     return requirements
#
# def read_file(file_path):
#     doc = Document(file_path)  # Mở file .docx
#     content = []
#
#     # Duyệt qua từng đoạn văn trong tài liệu
#     for paragraph in doc.paragraphs:
#         content.append(paragraph.text)  # Thêm nội dung đoạn văn vào danh sách
#
#     return '\n'.join(content)
#
# if __name__ == "__main__":
#     print("nhaapj vào tài liệu cần check")
#     file_path = "./DocumentBA/TÀI LIỆU NHẬP TRẢ XÁC PHASE 2.docx"
#     content = read_file(file_path)
#     requirements = extract_requirements_Vni(content)
#     print(requirements)

import google.generativeai as genai

genai.configure(api_key="AIzaSyAfKUpu655ilmSh5Qk6e9fx4qPyl1hK5rE")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"Methods: {model.supported_generation_methods}\n")