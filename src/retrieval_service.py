import os
from dotenv import load_dotenv
import httpx
from .models import Message
from .llm_utils import format_history
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
VECTORS_API_URL = os.getenv("VECTORS_API_URL", "http://127.0.0.1:8001")

if not api_key:
    print("WARNING: MISTRAL_API_KEY not found in .env")

client = Mistral(api_key=api_key)


async def build_retrieval_query(chat_history: list[Message], new_question: str) -> str:
    """
    Build a short retrieval-focused summary from recent chat history and the
    latest user question.
    """
    try:
        recent_history = chat_history[-12:]
        formatted_history = format_history(recent_history)

        system_instruction = """
You prepare retrieval queries for a veterinary knowledge database.

Your task:
Given the conversation history and the latest user question, write a short,
dense, factual summary containing only the details needed to understand the
latest question and retrieve relevant veterinary references.

Rules:
- Do NOT answer the clinical question.
- Do NOT invent or assume missing facts.
- Do NOT include explanations or advice.
- Do NOT include greetings or filler text.
- Keep the output short and information-dense.
- Output plain text only.
- If the last user question is fully understandable without prior history,
  return a concise reformulation of that question for retrieval.
"""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(formatted_history)
        messages.append({"role": "user", "content": new_question})

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.1,
        )

        content = response.choices[0].message.content

        if isinstance(content, list):
            content = " ".join(
                part.text for part in content
                if hasattr(part, "text") and part.text
            )

        if not content or not str(content).strip():
            return new_question.strip()

        return str(content).strip()

    except Exception as e:
        print(f"Retrieval query generation error: {e}")
        return new_question.strip()



async def retrieve_relevant_chunks(retrieval_query: str) -> list[str]:

    cleaned_query = retrieval_query.strip()

    if not cleaned_query:
        return []

    url = f"{VECTORS_API_URL}/retrieve"
    payload = {"query": cleaned_query}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            return []

        results = data.get("results", [])

        if not isinstance(results, list):
            return []

        safe_results = [
            item.strip()
            for item in results
            if isinstance(item, str) and item.strip()
        ]

        return safe_results

    except Exception as e:
        print(f"Vectors retrieval error: {e}")
        return []