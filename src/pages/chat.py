import reflex as rx
from ..state import State


def chat_page() -> rx.Component:
    return rx.hstack(
        # ======= LEFT SIDEBAR =======
        rx.vstack(
            # New Chat Button
            rx.button(
                rx.hstack(
                    rx.icon("plus", size=18),
                    rx.text("New Chat"),
                    spacing="2"
                ),
                on_click=State.create_new_chat,
                width="100%",
                background_color="#2A2B32",
                color="white",
                _hover={"background_color": "#40414F"}
            ),


            # Thread List
            rx.vstack(
                rx.foreach(
                    State.threads,
                    lambda thread: rx.hstack(
                        # Thread Title (clickable)
                        rx.text(
                            thread.title,
                            color="white",
                            cursor="pointer",
                            flex="1",
                            on_click=lambda: State.select_thread(thread.id),
                            _hover={"color": "#10a37f"}
                        ),


                        # Delete Button
                        rx.icon(
                            "trash-2",
                            size=16,
                            color="gray",
                            cursor="pointer",
                            on_click=lambda: State.delete_thread(thread.id),
                            _hover={"color": "red"}
                        ),


                        width="100%",
                        padding="10px",
                        border_radius="5px",
                        _hover={"background_color": "#2A2B32"},
                        justify="between",
                        align="center"
                    )
                ),
                width="100%",
                spacing="1",
                overflow_y="auto"
            ),


            width="260px",
            height="100vh",
            background_color="#202123",
            padding="15px",
            spacing="4",
            border_right="1px solid #4d4d4f"
        ),


        # ======= MAIN CHAT AREA =======
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("src AI", size="6", color="white"),
                rx.spacer(),
                rx.button(
                    "Logout",
                    on_click=State.logout,
                    background_color="#ef4444",
                    color="white",
                ),
                width="100%",
                padding="20px",
                background_color="#343541",
                border_bottom="1px solid #4d4d4f"
            ),


            # Chat Messages Area
            rx.vstack(
                rx.cond(
                    State.current_thread,
                    # Show messages if thread is selected
                    rx.vstack(
                        rx.foreach(
                            State.chat_history,
                            lambda msg:rx.fragment(
                                rx.box(
                                    rx.markdown(
                                        msg.text,
                                        color="white"
                                    ),
                                    background_color=rx.cond(
                                        msg.is_user,
                                        "#10a37f",  # Green for user
                                        "#444654"   # Grey for AI
                                    ),
                                    padding="15px",
                                    border_radius="10px",
                                    max_width="70%",
                                    align_self=rx.cond(msg.is_user, "end", "start")
                                ),
                                rx.cond(
                                    msg.is_user,
                                    rx.box(id="last-user-msg", height="0px"),
                                    rx.fragment()
                                )
                            )
                        ),
                        width="100%",
                        spacing="4"
                    ),
                    # Show welcome message if no thread selected
                    rx.center(
                        rx.vstack(
                            rx.icon("message-circle", size=48, color="gray"),
                            rx.text(
                                "Select a chat or start a new one",
                                color="gray",
                                font_size="18px"
                            ),
                            spacing="3",
                            align="center"
                        ),
                        height="100%",
                        width="100%"
                    )
                ),
                width="100%",
                padding="20px",
                overflow_y="auto",
                flex="1",
                id="messages-container"
            ),


            # ======= INPUT AREA (With Status Text) =======
            rx.vstack(
                # The "Thinking..." Text
                rx.cond(
                    State.is_processing,
                    rx.box(
                        rx.text(
                            "src is thinking...",
                            color="#10a37f",
                            font_size="12px",
                            font_weight="bold"
                        ),
                        width="100%",
                        padding_left="20px",
                        padding_bottom="5px",
                        background_color="#343541"
                    )
                ),

                # 2. The Input Bar
                rx.hstack(
                    rx.input(
                        placeholder="Type your veterinary question...",
                        value=State.input_text,
                        on_change=State.set_input_text,
                        on_key_down=lambda key: rx.cond(
                            key == "Enter",
                            State.send_message,
                            rx.noop()
                        ),
                        width="100%",
                        height="50px",
                        variant="soft",
                        color_scheme="gray",
                        style={
                            "background_color": "#40414f",
                            "color": "white",
                            "font_size": "16px",
                            "padding_top": "12px",
                            "padding_bottom": "12px",
                            "padding_left": "15px",
                        },
                    ),
                    rx.button(
                        rx.icon("send", size=18),
                        on_click=State.send_message,
                        background_color="#10a37f",
                        color="white",
                        height="50px",
                        width="50px",
                        border_radius="5px",
                        _hover={"background_color": "#0d8a6a"}
                    ),
                    width="100%",
                    padding="20px",
                    padding_top="5px",
                    background_color="#343541",
                    spacing="3",
                    align_items="center"
                ),

                width="100%",
                spacing="0",
                background_color="#343541"
            ),


            width="100%",
            height="100vh",
            background_color="#343541",
            spacing="0"
        ),


        spacing="0",
        width="100%",
        on_mount=[State.check_login, State.load_threads]
    )
