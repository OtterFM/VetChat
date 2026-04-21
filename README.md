# VetChat
___

## Overview

VetChat is an AI chat application built with Python, Reflex, and SQLModel 
for veterinary professionals in Greece. It combines a clean chat interface
with authentication, saved conversation threads, and retrieval-augmented AI responses.  

To support retrieval, the app passes the latest question and recent chat history
to an LLM, which rephrases the user’s query into a short, context-preserving retrieval query.
The rephrased query is then used to retrieve relevant chunks through Vet Notes RAG.

***

## Features

- Secure user login and logout.
- Save chat conversations in separate threads.
- Show previous chats in sidebar.
- Start new chat or delete old one.
- Use LLM Mistral Small to answer veterinary questions.
- Retrieve relevant veterinary knowledge before answering.

***

## Project Structure
```text
VetChat/
├── src/
│   ├── pages/                  # Main UI pages
│   │   ├── chat.py             # Chat page
│   │   └── login.py            # Log in page
│   ├── state/                  # App state
│   │   ├── auth.py             # Login, logout, session management
│   │   ├── chat.py             # Chat operations (threads, creation of new chats, messages)
│   │   └── chat_service.py     # Helper functions for chat tasks
│   ├── models.py               # Securite helpers + Database models
│   ├── llm_utils.py            # Formats messages to Mistral's format
│   ├── retrieval_service.py    # Retrieves relevant chunks based on user's query
│   └── ai_service.py           # Main communication point with LLM
└── add_user.py                 # Helper to add user to db
```

***

## Requirements
### Python
Python 3.11.9
### Python packages
```pip install -r requirements.txt```
### Environmental Variables
- **Mistral API key**: Set `MISTRAL_API_KEY` in `.env` file.
- **RAG URL**: Optionally set `VECTORS_API_URL` in `.env` file. Ensure Vet Notes RAG is running. 
### Database setup
- Initialize and migrate the database:
   ```bash
   reflex db init
   reflex db makemigrations
   reflex db migrate
   ```
- Run `add_user.py` to create user(s) before logging in.

***

## Installation
1. Clone the repo.
2. Create virtual environment.
3. Install packages.
4. Create `.env`.
5. Ensure Vet Notes RAG is running.
6. Set up the database.
7. Start Reflex app: Run `reflex run`.
8. Open local url shown in terminal and log in.

***

## Usage

1. Open app in browser.
2. Log in with username and password you created.
3. If no previous threads, a new one will start automatically. Else select from the sidebar or click **New Chat**.
4. Type veterinary related message in message box.
5. Press Enter or click the send button.
6. Wait for AI response.
7. Use the sidebar to switch between chats or delete a thread if needed.

***

## Notes and Limitations

VetChat is designed to support veterinary professionals and is not
a replacement for clinical judgment.

When relevant, it prioritizes Greece/EU medication availability and metric units.
If the available information is insufficient, the system may ask clarifying questions first.

Before first use, the database must be migrated and at least one user must be created
with `add_user.py`.
