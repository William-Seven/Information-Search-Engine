import os
import json

# 修改为相对路径
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'homework2')
EVAL_PATH = os.path.join(BASE_DIR, "manual_eval.json")


def compute_precision_at_k(results, k=5):
    top_k = results[:k]
    relevant_count = sum([r['relevant'] for r in top_k])
    return relevant_count / k


def main():
    if not os.path.exists(EVAL_PATH):
        print(f"Evaluation file not found: {EVAL_PATH}")
        return

    with open(EVAL_PATH, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)

    print("Evaluation Results (Precision@5):\n" + "-" * 40)
    precisions = []

    for item in eval_data:
        query = item['query']
        results = item['results']
        p_at_5 = compute_precision_at_k(results, k=5)
        precisions.append(p_at_5)
        print(f"Query: {query}")
        print(f"Precision@5: {p_at_5:.2f}")
        print("-" * 40)

    if precisions:
        avg = sum(precisions) / len(precisions)
        print(
            f"\nAverage Precision@5 over {len(precisions)} queries: {avg:.2f}")
    else:
        print("No evaluation records found.")


if __name__ == "__main__":
    main()