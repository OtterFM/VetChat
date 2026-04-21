import reflex as rx
from ..state import State


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(
                "src",
                size="9",
                weight="bold",
                color="#d1d5db",
                font_family='system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif',
                letter_spacing="-1px",
            ),

            rx.spacer(height="20px"),

            rx.vstack(
                rx.cond(
                    State.error_message != "",
                    rx.text(State.error_message, color="red", font_size="sm")
                ),
                rx.input(
                    placeholder="Username",
                    on_change=State.set_username,
                    width="100%",
                    size="3",
                    variant="surface",
                    background_color="#374151",
                    color="white",
                    border_color="#4b5563",
                    _placeholder={"color": "#9ca3af"},
                ),
                rx.input(
                    type="password",
                    placeholder="Password",
                    on_change=State.set_password,
                    width="100%",
                    size="3",
                    variant="surface",
                    background_color="#374151",
                    color="white",
                    border_color="#4b5563",
                    _placeholder={"color": "#9ca3af"},
                ),
                rx.button(
                    "Log in",
                    on_click=State.login,
                    width="100%",
                    size="3",
                    background_color="#10a37f",
                    color="white",
                    _hover={"background_color": "#1a7f64"},
                    cursor="pointer",
                ),
                spacing="4",
                width="100%",
            ),

            bg="#1f2937",
            padding="40px",
            border_radius="12px",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.5)",
            width=["90%", "90%", "350px"],
            max_width="350px",
            align_items="center",
            spacing="5",
            border="1px solid #374151",
        ),
        width="100%",
        height="100vh",
        background_color="#111827",
        padding="20px",
    )
