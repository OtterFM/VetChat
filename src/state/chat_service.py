from datetime import datetime
from ..models import ChatThread, Message

def check_rate_limit(last_time: datetime | None, cooldown_seconds: int) -> bool:
    """Returns True if user is allowed to send message (cooldown passed)."""
    if not last_time:
        return True

    now = datetime.utcnow()
    time_since_last = (now - last_time).total_seconds()
    return time_since_last >= cooldown_seconds


def ensure_thread(session, user_id: int, current_thread_id: int | None) -> ChatThread:
    """Gets existing thread or creates a new one if ID is missing."""
    if current_thread_id:
        return session.get(ChatThread, current_thread_id)

    new_thread = ChatThread(user_id=user_id)
    session.add(new_thread)
    session.commit()
    session.refresh(new_thread)
    return new_thread

def save_message(session, thread_id: int, text: str, is_user: bool) -> Message:
    """Saves a single message to the database."""
    msg = Message(
        thread_id=thread_id,
        text=text,
        is_user=is_user
    )
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


def update_thread_title(session, thread_id: int, first_question: str):
    """Renames thread based on the first question."""
    # Check if this is the very first user message
    count = session.exec(
        Message.select()
        .where(Message.thread_id == thread_id, Message.is_user == True)
    ).all()

    if len(count) == 1:
        thread = session.get(ChatThread, thread_id)
        if thread:
            thread.title = first_question[:30] + ("..." if len(first_question) > 30 else "")
            session.add(thread)
            session.commit()

def get_history(session, thread_id: int) -> list[Message]:
    """Fetches chat history excluding the very latest message."""
    return session.exec(
        Message.select()
        .where(Message.thread_id == thread_id)
        .order_by(Message.created_at)
    ).all()

