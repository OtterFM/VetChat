import reflex as rx
from datetime import datetime
from ..models import ChatThread, Message
from .auth import AuthState
from ..ai_service import get_ai_response
from . import chat_service


class ChatState(AuthState):
    """Chat sub-state - inherits from AuthState and handles chat operations"""
    is_processing: bool = False
    threads: list[ChatThread] = []
    current_thread_id: int = 0
    current_thread: ChatThread | None = None
    chat_history: list[Message] = []
    input_text: str = ""
    last_message_time: datetime | None = None
    MESSAGE_COOLDOWN_SECONDS = 1  # Minimum seconds between messages

    def set_input_text(self, value: str):
        self.input_text = value

    def load_threads(self):
        """Load all threads for the sidebar"""
        if not self.current_user:
            return
        with rx.session() as session:
            self.threads = session.exec(
                ChatThread.select()
                .where(ChatThread.user_id == self.current_user.id)
                .order_by(ChatThread.created_at.desc())
            ).all()

            # If user has no threads, create the first one with welcome message
            if not self.threads:
                new_thread = ChatThread(user_id=self.current_user.id)
                session.add(new_thread)
                session.commit()
                session.refresh(new_thread)

                thread_id = new_thread.id

                # Add initial assistant message
                initial_msg = Message(
                    thread_id=thread_id,
                    text="Hello! I'm your assistant for anything regarding Veterinary Medicine.\n\nNote: I do not substitute professional opinion.",
                    is_user=False
                )
                session.add(initial_msg)
                session.commit()

            # Get fresh threads list after potential creation
            self.threads = session.exec(
                ChatThread.select()
                .where(ChatThread.user_id == self.current_user.id)
                .order_by(ChatThread.created_at.desc())
            ).all()

        # After session closes, select first thread if none selected
        if self.threads and not self.current_thread:
            self.select_thread(self.threads[0].id)

    def select_thread(self, thread_id: int):
        """User clicked a sidebar thread"""
        with rx.session() as session:
            thread = session.get(ChatThread, thread_id)
            if thread:
                self.current_thread = thread
                self.current_thread_id = thread.id
        self.load_messages()

    def create_new_chat(self):
        """User clicked '+ New Chat' button"""
        if not self.current_user:
            return
        with rx.session() as session:
            new_thread = ChatThread(user_id=self.current_user.id)
            session.add(new_thread)
            session.commit()
            session.refresh(new_thread)

            # Add initial assistant message
            initial_msg = Message(
                thread_id=new_thread.id,
                text="Hello! I'm your assistant for anything regarding Veterinary Medicine.\n\nNote: I do not substitute professional opinion.",
                is_user=False
            )
            session.add(initial_msg)
            session.commit()

            self.current_thread = new_thread
            self.load_messages()
            self.load_threads()

    def delete_thread(self, thread_id: int):
        """User clicked trash icon"""
        with rx.session() as session:
            thread = session.get(ChatThread, thread_id)

            # Messages will be deleted automatically by the model rule
            if thread:
                session.delete(thread)
                session.commit()

        # If we deleted the currently active thread, clear it
        if self.current_thread and self.current_thread.id == thread_id:
            self.current_thread = None
            self.chat_history = []

        self.load_threads()

    def load_messages(self):
        """Load messages for the current thread"""
        if not self.current_thread_id:
            self.chat_history = []
            return

        with rx.session() as session:
            self.current_thread = session.get(ChatThread, self.current_thread_id)
            self.chat_history = session.exec(
                Message.select()
                .where(Message.thread_id == self.current_thread_id)
                .order_by(Message.created_at)
            ).all()

    def _show_user_message_optimistically(self, text: str):
        """Immediately show user's message in UI before saving to DB"""
        temp_msg = Message(
            thread_id=self.current_thread_id if self.current_thread_id else 0,
            text=text,
            is_user=True,
            created_at=datetime.utcnow()
        )
        self.chat_history.append(temp_msg)
        self.input_text = ""

    async def send_message(self):
        """User hits Send button"""
        if not self.input_text or not self.current_user:
            return

        # Rate limiting: prevent spam
        if not chat_service.check_rate_limit(self.last_message_time, self.MESSAGE_COOLDOWN_SECONDS):
            return

        self.last_message_time = datetime.utcnow()

        question_text = self.input_text
        self._show_user_message_optimistically(question_text)

        self.is_processing = True
        yield

        with rx.session() as session:
            # Ensure Thread Exists
            curr_id = self.current_thread_id if self.current_thread_id != 0 else None
            thread = chat_service.ensure_thread(session, self.current_user.id, curr_id)
            self.current_thread_id = thread.id

            history = chat_service.get_history(session, thread.id)

            chat_service.save_message(session, thread.id, question_text, is_user=True)

            chat_service.update_thread_title(session, thread.id, question_text)

            ai_text = await get_ai_response(history, question_text)

            chat_service.save_message(session, thread.id, ai_text, is_user=False)

        self.is_processing = False

        # Refresh UI
        self.load_messages()
        self.load_threads()
        self.input_text = ""

        # Scroll to bottom ! Future: maybe change 100ms !
        yield rx.call_script("""
            setTimeout(() => {
                const target = document.getElementById('last-user-msg');
                if(target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100)
        """)

    def logout(self):
        """Override logout to also clear chat state"""
        self.chat_history = []
        self.threads = []
        self.current_thread = None
        self.input_text = ""

        # Call parent's logout
        return super().logout()
