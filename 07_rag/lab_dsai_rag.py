import json
import os
import runpy

import pandas as pd
import requests


MODEL = "smollm2:1.7b"
PORT = 11434
OLLAMA_HOST = f"http://localhost:{PORT}"
CHAT_URL = f"{OLLAMA_HOST}/api/chat"
DOCUMENT = "data/dsai_project_notes.csv"
OUTPUT_PATH = "lab_dsai_rag_output.md"


def ensure_workdir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)


def start_ollama():
    ollama_script_path = os.path.join(os.getcwd(), "01_ollama.py")
    runpy.run_path(ollama_script_path)


def search_project_notes(query, document_path, limit=5):
    df = pd.read_csv(document_path)

    text_columns = ["topic", "goal", "tools", "deliverable", "keywords"]
    terms = [
        term.lower()
        for term in query.replace("?", "").split()
        if len(term) >= 4
    ]
    mask = pd.Series(False, index=df.index)
    for column in text_columns:
        column_text = df[column].fillna("").str.lower()
        for term in terms:
            mask = mask | column_text.str.contains(term, na=False)

    results = df.loc[mask].head(limit)

    return {
        "query": query,
        "document": os.path.basename(document_path),
        "matches": results.to_dict(orient="records"),
        "num_matches": int(len(results)),
    }


def agent_run(role, task, model=MODEL):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": role},
            {"role": "user", "content": task},
        ],
        "stream": False,
    }
    response = requests.post(CHAT_URL, json=body, timeout=120)
    response.raise_for_status()
    return response.json()["message"]["content"]


def main():
    ensure_workdir()
    start_ollama()

    query = "How can I build a dashboard that answers questions with project documents?"
    retrieval = search_project_notes(query, DOCUMENT)
    retrieval_json = json.dumps(retrieval, indent=2)

    print("Testing search function...")
    print(f"Found {retrieval['num_matches']} matching records")
    print(retrieval_json)
    print()

    role = (
        "You are a helpful project planning assistant. "
        "Use only the retrieved project records provided by the user. "
        "Write a markdown response with a short title, a one-sentence summary, "
        "and bullet points explaining which project components are most relevant. "
        "If the retrieved data is incomplete, say what is missing."
    )

    result = agent_run(role=role, task=retrieval_json, model=MODEL)

    final_output = "\n".join(
        [
            "# Lab RAG Output",
            "",
            "## Query",
            query,
            "",
            "## Retrieved Records",
            "```json",
            retrieval_json,
            "```",
            "",
            "## Model Response",
            result,
            "",
        ]
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_output)

    print("Generated response:")
    print(result)
    print()
    print(f"Saved output to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
