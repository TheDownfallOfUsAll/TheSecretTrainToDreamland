# The Secret Train to Dreamland

## About

The Secret Train to Dreamland is a Streamlit fantasy storytelling application that combines:

- a long-form 25-page storybook experience
- account-based access and profile management
- AI chat personas (AC and Nikolai)
- local persistence with SQLite
- themed UI with story navigation and character visuals

Recent updates include expanded long-read story content, richer navigation sections, profile and settings pages, image-backed character sections, and OpenAI-powered chatbot responses with fallback behavior.

## Current App Sections

- Home
- Login
- Register
- Profile
- Settings
- Logout
- Characters List
- Storytelling
- Table of Story Contents
- Story (Pages 1-25)
- AI Fairy Chatbot
- About

## Enterprise System Features Used In This App

- Authentication and account lifecycle:
  - user registration, login, and logout flow
  - credential hashing with `sha256`
- Role-like gated access:
  - AI chat usage is gated behind login
- Persistent data layer:
  - SQLite database (`dreamland.db`)
  - schema initialization and migration-safe column backfill
- User profile management:
  - editable full name, bio, and profile image selection
- Stateful session management:
  - Streamlit `session_state` for user identity, chat flow, and page state
- Audit-like conversational persistence:
  - per-user chat history storage and reload
  - user-level chat history clearing controls
- External AI service integration:
  - OpenAI API integration for live responses
  - safe local fallback when API key is missing/unavailable
- Input policy controls:
  - blocked-word filter for chatbot inputs
- Modular app structure:
  - clear section-based navigation and isolated logic blocks

## Installation and Setup

### 1. Prerequisites

- Python 3.11+ recommended
- Windows PowerShell (examples below use PowerShell)

### 2. Clone or Download Project

If using git:

```bash
git clone <your-repo-url>
cd TheSecretTrainToDreamland
```

Or download and extract the project ZIP, then open a terminal in the project folder.

### 3. Create Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

PowerShell:

```bash
.\.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install --upgrade pip
pip install streamlit openai
```

### 6. Configure Environment Variable (OpenAI)

PowerShell (current terminal session):

```bash
$env:OPENAI_API_KEY="your_api_key_here"
```

Optional persistent setup (new terminals):

```bash
setx OPENAI_API_KEY "your_api_key_here"
```

### 7. Run the App

```bash
streamlit run app.py
```

### 8. First Run Notes

- SQLite file `dreamland.db` is auto-created on first run.
- Register a new account, then login to use persisted AI Fairy chat history.
- If OpenAI key is missing, chatbot continues with local persona fallback replies.

## Database Summary

- Database file: `dreamland.db`
- Tables:
  - `users`
  - `chat_history`

## Troubleshooting

- If images do not show:
  - confirm image files exist in the project root
  - restart Streamlit after file changes
- If OpenAI chat is not responding with live AI:
  - verify `OPENAI_API_KEY` is set in the same terminal session
- If dependencies fail:
  - confirm venv is activated
  - upgrade pip and reinstall requirements

## Tech Stack

- Python
- Streamlit
- SQLite
- OpenAI API

