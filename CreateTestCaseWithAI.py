import google.generativeai as genai
import configparser
import spacy
from spacy.matcher import Matcher
from docx import Document
import argparse


# Thêm config đọc API key
def load_gemini_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    genai.configure(api_key=config['GEMINI']['API_KEY'])


# Khởi tạo model Gemini
gemini_model = genai.GenerativeModel('gemini-pro')

#prompt advance
# prompt = f"""
# Hãy làm theo các bước sau để tạo test case:
#
# 1. Phân tích yêu cầu nghiệp vụ:
# 2. Xác định các điều kiện tiên quyết
# 3. Liệt kê các bước thực hiện chính xác
# 4. Xác định kết quả mong đợi
# 5. Định dạng theo chuẩn Gherkin với các keyword: Given, When, Then, And
#
# Tạo 3 test case variants cho các trường hợp:
# - Happy path
# - Boundary case
# - Error case
#
# Đầu ra phải là tiếng Việt và định dạng markdown
# """

#Function excuse for prompt advance
# def parse_gemini_response(response_text):
#     test_cases = []
#     current_case = {}
#
#     for line in response_text.split('\n'):
#         line = line.strip()
#
#         if line.startswith('**Scenario'):
#             if current_case:
#                 test_cases.append(current_case)
#             current_case = {
#                 "scenario": line.replace('**', '').strip(),
#                 "steps": [],
#                 "expected_result": ""
#             }
#         elif line.startswith(('Given', 'When', 'Then', 'And')):
#             current_case["steps"].append(line)
#             if line.startswith('Then'):
#                 current_case["expected_result"] = line.replace('Then', '').strip()
#
#     if current_case:
#         test_cases.append(current_case)
#
#     return test_cases[0] if test_cases else {}

# Sửa hàm generate_test_cases để tích hợp AI
def generate_test_cases(requirements):
    test_cases = []
    for idx, req in enumerate(requirements, 1):
        try:
            # Tạo prompt cho Gemini
            prompt = f"""
            Hãy tạo test case Gherkin cho yêu cầu nghiệp vụ sau:
            Yêu cầu: {req}
            Định dạng mong muốn:
            Scenario: [Tên scenario]
            Given [Điều kiện tiên quyết]
            When [Hành động]
            Then [Kết quả mong đợi]
            """

            # Gọi API Gemini
            response = gemini_model.generate_content(prompt)

            # Xử lý kết quả
            if response.text:
                test_case = parse_gemini_response(response.text)
                test_case["id"] = f"TC_{idx}"
                test_case["original_requirement"] = req
                test_cases.append(test_case)

        except Exception as e:
            print(f"Lỗi khi gen test case cho requirement {idx}: {str(e)}")

    return test_cases


def parse_gemini_response(response_text):
    # Phân tích kết quả từ Gemini
    test_case = {
        "scenario": "",
        "steps": [],
        "expected_result": ""
    }

    current_key = None
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith("Scenario:"):
            test_case["scenario"] = line.replace("Scenario:", "").strip()
        elif line.startswith(("Given", "When", "Then", "And")):
            test_case["steps"].append(line)
            if line.startswith("Then"):
                test_case["expected_result"] = line.replace("Then", "").strip()

    return test_case

def read_ba_document(file_path):
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format")

def extract_requirements(doc):
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)

    # Define patterns for requirement detection
    patterns = [
        [{"LOWER": "must"}, {"LOWER": "be"}, {"LOWER": "able"}, {"LOWER": "to"}, {"POS": "VERB"}],
        [{"LOWER": "should"}, {"LOWER": "be"}, {"LOWER": "able"}, {"LOWER": "to"}, {"POS": "VERB"}],
        [{"LOWER": "requires"}, {"LOWER": "that"}, {"POS": "PRON"}, {"POS": "VERB"}],
        [{"LOWER": "hệ"}, {"LOWER": "thống"}, {"LOWER": "phải"}, {"LOWER": "có"}, {"LOWER": "khả"},
         {"LOWER": "năng"}, {"POS": "VERB"}],
        # Pattern 2: "Phải [động từ]..."
        [{"LOWER": "phải"}, {"POS": "VERB"}],
        # Pattern 3: "Cần phải [động từ]..."
        [{"LOWER": "cần"}, {"LOWER": "phải"}, {"POS": "VERB"}],
        # Pattern 4: "Yêu cầu [động từ]..."
        [{"LOWER": "yêu"}, {"LOWER": "cầu"}, {"POS": "VERB"}],
        # Pattern 5: "Khi [người dùng/hệ thống] [động từ]..."
        [{"LOWER": "khi"}, {"LOWER": {"in": ["người", "hệ"]}}, {"POS": "VERB"}]
    ]

    for idx, pattern in enumerate(patterns):
        matcher.add(f"REQUIREMENT_{idx}", [pattern])

    requirements = []
    for sent in doc.sents:
        matches = matcher(sent)
        if matches:
            requirements.append(sent.text)
    return requirements

# def generate_test_cases(requirements):
#     test_cases = []
#     for idx, req in enumerate(requirements, 1):
#         doc = nlp(req)
#         test_case = {
#             "id": f"TC_{idx}",
#             "scenario": f"Verify {req}",
#             "steps": [],
#             "expected_result": f"System {req.split(' must ')[0]} correctly"
#         }
#
#         # Extract actions and inputs using dependency parsing
#         actions = [token.lemma_ for token in doc if token.pos_ == "VERB"]
#         inputs = [ent.text for ent in doc.ents if ent.label_ in ["INPUT", "DATA"]]
#
#         # Build steps (simplified example)
#         test_case["steps"].append(f"Given the user is on the relevant page")
#         if actions:
#             test_case["steps"].append(f"When the user performs {actions[0]}")
#         if inputs:
#             test_case["steps"].append(f"And provides {', '.join(inputs)}")
#
#         test_cases.append(test_case)
#     return test_cases


def export_to_gherkin(test_cases, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for tc in test_cases:
            f.write(f"Scenario: {tc['scenario']}\n")
            for step in tc['steps']:
                f.write(f"  {step}\n")
            f.write(f"  Then {tc['expected_result']}\n\n")


if __name__ == "__main__":
    # how to run file : python CreateTestCaseWithAI.py --input <đường_dẫn_file_input> [--output <đường_dẫn_file_output>]
    load_gemini_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to BA document", required=True)
    parser.add_argument("--output", help="Output file path", default="test_cases.feature")
    args = parser.parse_args()

    # Process document
    text = read_ba_document(args.input)
    print("sau khi đọc xong file")
    print(text)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Generate test cases
    requirements = extract_requirements(doc)
    print(requirements)
    # test_cases = generate_test_cases(requirements)
    #
    # # Export to Gherkin
    # export_to_gherkin(test_cases, args.output)
    # print(f"Generated {len(test_cases)} test cases in {args.output}")