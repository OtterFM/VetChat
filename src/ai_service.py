import os
from dotenv import load_dotenv
from mistralai.client import Mistral
from .models import Message
from .llm_utils import format_history
from .retrieval_service import build_retrieval_query, retrieve_relevant_chunks

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    print("WARNING: GEMINI_API_KEY not found in .env")

client = Mistral(api_key=api_key)


def build_final_user_message(new_question: str, retrieved_chunks: list[str]) -> str:
    """
    Build final user message with chunks appended.
    """
    cleaned_question = new_question.strip()

    if not retrieved_chunks:
        return cleaned_question

    formatted_chunks = "\n\n".join(
        f"Chunk {index + 1}:\n{chunk.strip()}"
        for index, chunk in enumerate(retrieved_chunks)
        if isinstance(chunk, str) and chunk.strip()
    )

    if not formatted_chunks:
        return cleaned_question

    return (
        f"User question:\n{cleaned_question}\n\n"
        "# Retrieved veterinary context\n"
        "If relevant and accurate, use the following retrieved notes as supporting context.\n"
        "Do not treat them as guaranteed correct. Ignore anything irrelevant, low-confidence, or contradictory.\n\n"
        f"{formatted_chunks}"
    )


async def get_ai_response(chat_history: list[Message], new_question: str) -> str:
    """
    Main function to call mistral AI.
    """
    try:
        formatted_history = format_history(chat_history)

        retrieval_query = await build_retrieval_query(chat_history, new_question)
        retrieved_chunks = await retrieve_relevant_chunks(retrieval_query)
        final_user_message = build_final_user_message(new_question, retrieved_chunks)

        system_instruction= """
        # ROLE
        You are an expert Certified Veterinary Specialist consulting
        EXCLUSIVELY with licensed small animal VETERINARIANS in Greece.

        # SAFETY & ACCURACY PROTOCOL
        - NEVER invent drug dosages, treatment protocols, or clinical data.
        - NO GUESSING: If you do not have enough clinical information to form a solid opinion,
        you MUST ask clarifying questions first.
        - If uncertain, EXPRESS UNCERTAINTY.
        - If a question is outside veterinary medicine, politely redirect to veterinary topics.
        
        # USE OF RETRIEVED CONTEXT
        - Retrieved notes may be relevant but are not guaranteed to be correct.
        - Use retrieved context only if it is relevant to the current case and consistent with the user question.
        - Ignore retrieved content that appears irrelevant, contradictory, or insufficiently specific.

        # LOCATION (GREECE/EU)
        - LANGUAGE: IF asked in Greek, answer in Greek.
        - REGULATION: When discussing medications, prioritize drugs and formulations available
        in Greece/EU.
        - UNITS: STRICTLY Metric (kg, mg, ml, °C).
        - DISEASE PREVALENCE: PRIORITIZE diseases endemic to Greece/Mediterranean in your differential diagnoses, if clinical signs match.
        """

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(formatted_history)
        messages.append({"role": "user", "content": final_user_message})

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
        )

        content = response.choices[0].message.content

        if isinstance(content, list):
            content = " ".join(
                part.text for part in content
                if hasattr(part, "text") and part.text
            )

        if not content or not str(content).strip():
            return "I apologize, but I could not generate a veterinary response right now."

        return str(content).strip()



    except Exception as e:
        print(f"Mistral API Error: {e}")
        return "I apologize, but I am unable to connect to the veterinary knowledge base right now."
