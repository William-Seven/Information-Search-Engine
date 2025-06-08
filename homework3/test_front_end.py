import requests
import json

# 定义目标 URL
url = "http://127.0.0.1:5000/feedback/check_incorrect"

# 测试用例列表
test_cases = [
    {
        "description": "正常请求，检查 'Description' 字段值是否曾被标记为不正确",
        "data": {
            "field": "Description",
            "value": "Individual animals differ in their responses to environmental challenges. Identifying these differences before animals are translocated could be a useful tool in improving postrelease success. For most species, however, uncertainty persists around which behaviours contribute to postrelease success. Greater bilbies, <em>Macrotis lagotis</em>, are a threatened species, for which detailed behavioural studies in situ are rare. We tested bilbies prior to their release to a fenced safe haven to examine whether (1) bilby response to a known threat (that is, human observer) and novelty (that is, novel scent) was individually different and repeatable, or alternatively plastic, and (2) if any behaviours were related to bilby fitness (breeding success and survival) postrelease. We found that several behaviours measured during trapping (exposure to a known threat) were individually variable and repeatable and that males that were less responsive (lower respiratory rate) during handling had greater breeding success (that is, the number of offspring sired relative to the opportunity to breed). Contrastingly, individual differences in bilby response to novel scents were not repeatable, but we did, however, find sex-specific responses in this context. Males took less time to initiate touch with the novel-scented object and touched the object more times than females, suggesting that males are less neophobic. Plasticity rather than personality predicted female post-release fitness. Females that were increasingly cautious of novelty had greater relative breeding success. Our study is the first to confirm repeatable and plastic behaviours in bilbies, develop a standardized test for prerelease screening of behaviours, and examine the fitness consequences of these behaviours. We encourage the use of the 'trap test' as a simple and practical way to screen bilbies for future conservation translocations. We also recommend further testing in environments where the risk of establishment failure may be higher (that is, invasive predators present) and where the fitness consequences may be more profound and thus detectable.\n\n\nContents:\n - R_code.zip"
        },
        "expected_status": 200,
        "expected_message": {"status": "success", "was_incorrect": True}
    },
    {
        "description": "正常请求，检查 'Title' 字段值是否曾被标记为不正确",
        "data": {
            "field": "Title",
            "value": "Data from: Predicting success of conservation translocations: Prerelease screening tools for a threatened marsupial"
        },
        "expected_status": 200,
        "expected_message": {"status": "success", "was_incorrect": False}
    },
    {
        "description": "缺少 'field' 字段",
        "data": {
            "value": "Data from: Predicting success of conservation translocations: Prerelease screening tools for a threatened marsupial"
        },
        "expected_status": 400,
        "expected_message": {"error": "请求体中缺少 'field' 或 'value' 字段"}
    },
    {
        "description": "缺少 'value' 字段",
        "data": {
            "field": "Title"
        },
        "expected_status": 400,
        "expected_message": {"error": "请求体中缺少 'field' 或 'value' 字段"}
    }
    # {
    #     "description": "请求不是 JSON 格式",
    #     "data": "not a json",
    #     "expected_status": 400,
    #     "expected_message": {"error": "请求必须是 JSON 格式"}
    # }
]


# 测试函数
def test_feedback_check_incorrect():
    for case in test_cases:
        print(f"测试用例: {case['description']}")
        headers = {"Content-Type": "application/json"}
        if isinstance(case['data'], dict):
            response = requests.post(url, headers=headers, json=case['data'])
        else:
            response = requests.post(url, headers=headers, data=case['data'])

        print(f"  状态码: {response.status_code}")
        print(f"  响应内容: {response.json()}")

        assert response.status_code == case[
            'expected_status'], f"状态码不匹配，期望 {case['expected_status']}，实际 {response.status_code}"
        assert response.json() == case[
            'expected_message'], f"消息不匹配，期望 {case['expected_message']}，实际 {response.json()}"
        print("  测试结果: 成功\n")


# 运行测试
if __name__ == "__main__":
    test_feedback_check_incorrect()