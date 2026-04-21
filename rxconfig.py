import reflex as rx

config = rx.Config(
    app_name="src",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)