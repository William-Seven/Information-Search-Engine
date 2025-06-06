import re
import json
import os

FEEDBACK_FILE = "manual_feedback.json"
OUTPUT_JSON_FILE = "extracted_data.json"


def save_feedback(field, value, correct):
    entry = {"field": field, "value": value, "correct": correct}
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as feedback_file:
            feedback_data = json.load(feedback_file)
    else:
        feedback_data = []
    feedback_data.append(entry)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as feedback_file:
        json.dump(feedback_data, feedback_file, indent=2, ensure_ascii=False)


def was_incorrect(field, value):
    if not os.path.exists(FEEDBACK_FILE):
        return False
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)
    for entry in feedback_data:
        if entry["field"] == field and entry["value"] == value and not entry["correct"]:
            return True
    return False


def extract_info_regex(text):
    info = {}

    # Regex extraction
    match = re.search(r"Title:\s*(.+)", text)
    if match:
        info["Title"] = match.group(1).strip()

    match = re.search(r"Authors:\s*(.+)", text)
    if match:
        info["Authors"] = [a.strip() for a in match.group(1).split(",")]
    else:
        info["Authors"] = []

    match = re.search(r"Keywords:\s*(.+)", text)
    if match:
        info["Keywords"] = [k.strip() for k in match.group(1).split(",")]

    match = re.search(r"Publication date:\s*([\d-]+)", text)
    if match:
        info["Publication Date"] = match.group(1)

    description_match = re.search(r"Description:\s*(.*?)(?:\Z)", text, re.DOTALL)
    if description_match:
        info["Description"] = description_match.group(1).strip()
    else:
        info["Description"] = ""

    url_pattern = re.compile(r'https?://[^\s"<]+|www\.[^\s"<]+')
    urls_found = url_pattern.findall(text)
    info["URLs"] = list(set(urls_found))

    doi_pattern = re.compile(r'10\.\d{4,9}/[^\s"<]+')
    dois_found = doi_pattern.findall(text)
    info["DOIs"] = list(set(dois_found))

    for url in info["URLs"]:
        if "github.com" in url:
            info["GitHub Link"] = url
            break

    for doi in info["DOIs"]:
        if "doi.org" in doi:
            info["DOI"] = doi
            break

    return info


def manual_evaluation(info_dict, input_file_name):
    print(f"\n--- 对文件 '{input_file_name}' 进行人工评价 ---")
    total_fields = 0
    correct_fields = 0

    for key, value in info_dict.items():
        value_str = str(value)
        if was_incorrect(key, value_str):
            print(f"⚠️ 该字段值曾被评为错误，注意检查：{value}")

        print(f"\n字段: {key}")
        print(f"抽取内容: {value}")
        while True:
            feedback = input("是否正确？(Y/N): ").strip().lower()
            if feedback in ['y', 'n']:
                break
            else:
                print("请输入 Y 或 N。")
        total_fields += 1
        is_correct = (feedback == 'y')
        if is_correct:
            correct_fields += 1
        save_feedback(key, value_str, is_correct)

    accuracy = correct_fields / total_fields if total_fields > 0 else 0
    print(f"\n✅ 文件 '{input_file_name}' 的人工评估准确率: {accuracy * 100:.2f}% ({correct_fields}/{total_fields})")
    return accuracy


if __name__ == "__main__":
    input_path = input("请输入文件路径或文件夹路径: ").strip()
    all_extracted_data = {}

    if os.path.isfile(input_path) and input_path.endswith(".txt"):
        files_to_process = [input_path]
    elif os.path.isdir(input_path):
        files_to_process = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".txt")]
    else:
        print("无效的输入路径。请输入一个 .txt 文件路径或一个包含 .txt 文件的文件夹路径。")
        exit()

    do_evaluation_global = input("\n是否对所有抽取结果进行人工评分？(Y/N): ").strip().lower() == 'y'

    for file_path in files_to_process:
        print(f"\n--- 处理文件: {file_path} ---")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            result = extract_info_regex(raw_text)

            file_name = os.path.basename(file_path)
            all_extracted_data[file_name] = result

            print("\n--- 抽取结果 ---")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if do_evaluation_global:
                manual_evaluation(result, file_name)

        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {e}")

    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_extracted_data, f, indent=2, ensure_ascii=False)
    print(f"\n所有抽取结果已保存到 {OUTPUT_JSON_FILE}")
