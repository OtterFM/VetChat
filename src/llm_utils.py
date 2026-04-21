from .models import Message

def format_history(db_messages: list[Message]) -> list[dict]:
    """
        Converts database messages into mistral's format.
    """
    history = []
    for msg in db_messages:
        role = "user" if msg.is_user else "assistant"
        history.append({
            "role": role,
            "content": msg.text,
        })
    return history