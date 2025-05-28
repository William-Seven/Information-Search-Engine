import os
import json
import pickle
import numpy as np
import spacy
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity

# 修改为相对路径
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")


def preprocess_query(text):
    text = BeautifulSoup(text, "html.parser").get_text()
    text = text.lower()
    doc = nlp(text)
    tokens = [
        token.lemma_.lower() for token in doc
        if token.is_alpha and token.lemma_.lower() not in STOP_WORDS
    ]
    return tokens


def load_index_data():
    with open(os.path.join(BASE_DIR, 'keys.json'), 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    with open(os.path.join(BASE_DIR, 'doc_vectors.json'), 'r', encoding='utf-8') as f:
        doc_vectors = json.load(f)
    with open(os.path.join(BASE_DIR, 'processed_docs.json'), 'r', encoding='utf-8') as f:
        docs = json.load(f)
    with open(os.path.join(BASE_DIR, 'inverted_index.json'), 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    with open(os.path.join(BASE_DIR, 'vectorizer.pkl'), 'rb') as f:
        vectorizer = pickle.load(f)
    return keywords, doc_vectors, docs, inverted_index, vectorizer


def save_evaluation(query, ranked_results, doc_map):
    eval_data = {
        "query": query,
        "results": []
    }

    print("\nPlease rate each result as relevant (1) or not relevant (0):")
    for i, (doc_id, sim) in enumerate(ranked_results):
        doc = doc_map[doc_id]
        print(f"\nResult {i+1}:")
        print(f"Title: {doc['title']}")
        print(f"Similarity: {sim:.2f}")
        while True:
            try:
                rel = int(input("Relevant? (1 = yes, 0 = no): "))
                if rel in [0, 1]:
                    break
            except ValueError:
                print("Invalid input. Please enter 1 or 0.")
        eval_data["results"].append({
            "doc_id": doc_id,
            "title": doc['title'],
            "score": round(sim, 4),
            "relevant": rel
        })

    save_path = os.path.join(BASE_DIR, "manual_eval.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(eval_data, f, indent=2, ensure_ascii=False)
    print(f"\nEvaluation saved to {save_path}")


def search(query, top_n=5):
    keywords, doc_vectors, docs, inverted_index, vectorizer = load_index_data()
    doc_vectors_matrix = np.array(list(doc_vectors.values()))
    doc_ids = list(doc_vectors.keys())

    query_tokens = preprocess_query(query)
    query_text = " ".join(query_tokens)
    raw_query_vector = vectorizer.transform([query_text])
    query_vector = np.zeros(len(keywords))

    vectorizer_vocab = vectorizer.get_feature_names_out()
    vocab_index = {word: i for i, word in enumerate(vectorizer_vocab)}
    for i, word in enumerate(keywords):
        if word in vocab_index:
            query_vector[i] = raw_query_vector[0, vocab_index[word]]

    if np.linalg.norm(query_vector) == 0:
        print("Query vector is all zeros, please enter a valid query.")
        return

    sims = cosine_similarity([query_vector], doc_vectors_matrix)[0]
    ranked = sorted(zip(doc_ids, sims), key=lambda x: -x[1])[:top_n]

    doc_map = {doc["filename"]: doc for doc in docs}
    for doc_id, sim in ranked:
        doc = doc_map.get(doc_id)
        if not doc:
            continue
        print(f"\nTitle: {doc['title']}")
        print(f"Authors: {doc['authors']}")
        print(f"Date: {doc['pub_date']}")
        print(f"Similarity: {sim:.2f}")

        matched_words = [
            token for token in query_tokens
            if token in inverted_index and doc_id in inverted_index[token]
        ]
        print(
            f"Matched Keywords: {', '.join(matched_words) if matched_words else 'None'}")

        desc = doc['raw_description']
        if matched_words:
            found = False
            for word in matched_words:
                idx = desc.lower().find(word)
                if idx != -1:
                    snippet = desc[max(0, idx-60):idx+80]
                    print(f"Snippet: ...{snippet}...")
                    found = True
                    break
            if not found:
                print("Snippet: (Matched word not found in raw description)")
        else:
            print("Snippet: (No matched keywords found in index)")

    save_evaluation(query, ranked, doc_map)


if __name__ == "__main__":
    while True:
        query = input("\nPlease enter your query (or 'q' to quit): ")
        if query.lower() in {"q", "quit", "exit"}:
            break
        search(query)