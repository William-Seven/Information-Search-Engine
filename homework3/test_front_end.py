import requests
import json

# Flask 应用的地址
BASE_URL = "http://127.0.0.1:5000"

# 测试文本
TEST_TEXT = """
Title: Machine Learning at Telescope Array

Authors: Kharuk, Ivan

Keywords: 

Publication date: 2025-03-12

Description:
Telescope Array is a large-scale cosmic-ray observatory studying ultra-high-energy cosmic rays. Its Surface Detector array consists of 507 scintillation stations arranged in a rectangular grid covering approximately 700 km&sup2;. This talk presents our deep learning approach to reconstructing cosmic ray properties from Telescope Array Surface Detector data. We demonstrate how combining multiple data representations with various neural architectures (convolutional, recurrent, and transformer networks) enhances reconstruction accuracy of primary particle properties, including arrival direction and energy. Finally, we present post-processing techniques developed for searching for rare event, such as ultra-high-energy photons.

Contents:
 - TA_ML_Delaware_final.pdf
"""

# 1. 测试 /extract 接口
def test_extract():
    print("Testing /extract endpoint...")
    response = requests.post(f"{BASE_URL}/extract", json={"text": TEST_TEXT})
    if response.status_code == 200:
        data = response.json()
        print("Extracted data:", data)
        return data["uuid"]
    else:
        print("Failed to extract data:", response.json())
        return None

# 2. 测试 /feedback 接口
def test_feedback(uuid):
    print("Testing /feedback endpoint...")
    feedback_data = [
        {"field": "Title", "correct": True},
        {"field": "Authors", "correct": False},
        {"field": "Keywords", "correct": True},
        {"field": "Publication Date", "correct": True},
        {"field": "Description", "correct": True},
        {"field": "GitHub Link", "correct": True},
        {"field": "DOI", "correct": True}
    ]
    for feedback in feedback_data:
        response = requests.post(f"{BASE_URL}/feedback", json={"uuid": uuid, "field": feedback["field"], "correct": feedback["correct"]})
        if response.status_code != 200:
            print("Failed to submit feedback:", response.json())
            return False
    print("Feedback submitted successfully.")
    return True

# 3. 测试 /history 接口
def test_history():
    print("Testing /history endpoint...")
    response = requests.post(f"{BASE_URL}/history", json={"Num": 5})
    if response.status_code == 200:
        data = response.json()
        print("History data:", data)
        return data["history"], data["correct_history"]
    else:
        print("Failed to get history:", response.json())
        return None, None

# 4. 测试总正确率计算
def test_accuracy(uuid):
    print("Testing accuracy calculation...")
    history_data, correct_history_data = test_history()
    if history_data and correct_history_data:
        for entry_uuid, entry_data in history_data.items():
            if entry_uuid == uuid:
                accuracy = entry_data.get("accuracy")
                correct_history = correct_history_data.get(entry_uuid, {})
                print(f"Accuracy for UUID {uuid}: {accuracy}")
                print(f"Correct history for UUID {uuid}: {correct_history}")
                return accuracy
    print("Failed to find accuracy for UUID:", uuid)
    return None

# 主测试函数
def main():
    print("Starting tests...")
    uuid = test_extract()
    if uuid:
        if test_feedback(uuid):
            accuracy = test_accuracy(uuid)
            if accuracy is not None:
                print("Test completed successfully.")
            else:
                print("Accuracy test failed.")
        else:
            print("Feedback test failed.")
    else:
        print("Extract test failed.")

if __name__ == "__main__":
    main()