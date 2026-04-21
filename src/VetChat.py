import reflex as rx
from .pages.login import login_page
from .pages.chat import chat_page

app = rx.App()
app.add_page(login_page, route="/", title="src | Log In")
app.add_page(chat_page, route="/chat", title="src | Chat")
