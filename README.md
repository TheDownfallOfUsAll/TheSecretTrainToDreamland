# 🚂 The Secret Train to Dreamland

## ✨ About

Welcome to **The Secret Train to Dreamland** — a fantasy storytelling app built with **Streamlit**.  
The app combines long-form reading, AI character chat, account-based features, and immersive visual design.

## 🆕 Recent Updates

- 🏠 **Home tab improved** with stronger hero visuals, quick metrics, and Start Here guidance
- 🔐 **Login / Register / Profile / Settings / Logout** UX refined with clearer prompts and status messages
- 👤 **Profile tab** now includes snapshot metrics (saved messages and profile image status)
- ⚙️ **Settings tab** improved with preference summary and account maintenance guidance
- 📘 **Story (Pages 1–25)** upgraded with long-read paragraphs and reading progress
- 🧚 **AI Fairy Chatbot** improved with clearer behavior notes and conversation turn count
- ℹ️ **About tab** expanded with platform highlights
- 🛡️ **Startup reliability improved**: app no longer crashes when `openai` package is missing
- 🌐 **Live deployment published** on Streamlit Community Cloud

## 🌌 App Overview

- 📖 Long-read **Storybook (Pages 1–25)** with expanded chapter narrative
- 🧚 AI Fairy Chatbot with alternating guides: **AC** and **Nikolai**
- 🔐 Authentication flow: Login, Register, Profile, Settings, Logout
- 💾 SQLite persistence for users and per-account chat history
- 🧠 OpenAI-powered chat responses with graceful local fallback
- 🎨 Fantasy interface with character imagery and themed navigation

## 🧭 Current App Sections

- 🏠 Home
- 🔐 Login
- 📝 Register
- 👤 Profile
- ⚙️ Settings
- 🚪 Logout
- 🌟 Characters List
- 📚 Storytelling
- 📑 Table of Story Contents
- 📘 Story (Pages 1-25)
- 🧚 AI Fairy Chatbot
- ℹ️ About

## 🏢 Enterprise System Features Used In This App

- ✅ **Authentication & Account Lifecycle**
  - Register, login, and logout flow
  - Credential hashing with `sha256`
- ✅ **Access Control**
  - AI Fairy Chatbot usage is gated behind login
- ✅ **Persistent Data Layer**
  - SQLite database (`dreamland.db`)
  - Schema initialization and migration-safe column backfill
- ✅ **User Profile Management**
  - Editable full name, bio, and profile image
- ✅ **Stateful Session Management**
  - `st.session_state` for user identity, chat speaker flow, and page state
- ✅ **Conversation Persistence**
  - Per-user chat history storage and reload
  - User-level chat clear controls
- ✅ **External AI Service Integration**
  - OpenAI API integration for live responses
  - Local fallback persona responses when API key is unavailable
  - Safe optional OpenAI import handling if package is not installed
- ✅ **Input Safety Controls**
  - Blocked-word filtering for chatbot input
- ✅ **Modular Sectioned App Architecture**
  - Isolated page sections and maintainable structure

## 🛠️ Installation & Setup

### 1. ✅ Prerequisites

- Python 3.11+ recommended
- Windows PowerShell (commands below use PowerShell syntax)

### 2. 📦 Get the Project

If using Git:

```bash
git clone <your-repo-url>
cd TheSecretTrainToDreamland
```

Or download the ZIP and open a terminal in the extracted folder.

### 3. 🧪 Create Virtual Environment

```bash
python -m venv .venv
```

### 4. ▶️ Activate Virtual Environment

```bash
.\.venv\Scripts\activate
```

### 5. 📥 Install Dependencies

```bash
pip install --upgrade pip
pip install streamlit openai
```

### 6. 🔑 Configure OpenAI API Key

Current terminal session:

```bash
$env:OPENAI_API_KEY="your_api_key_here"
```

Persistent for future terminals:

```bash
setx OPENAI_API_KEY "your_api_key_here"
```

### 7. 🚀 Run the App

```bash
streamlit run app.py
```

### 8. 🧾 First-Run Behavior

- `dreamland.db` is created automatically on first run
- Register and login to unlock persistent AI chat history
- If no OpenAI key is set, chatbot still works via local persona fallback
- If `openai` package is not installed, app still runs using fallback mode

## ⚙️ Tech Stack

- 🐍 Python
- 🎈 Streamlit
- 🗄️ SQLite
- 🤖 OpenAI API

## 📝 Notes

- 📁 Keep image files in the project root for reliable rendering
- 💬 AI chat history is stored per logged-in account
- 🔄 Restart Streamlit after major file/style updates if UI seems stale
- 🛡️ Built-in filtered word checks are enabled in chatbot flow
- 🧩 OpenAI dependency is optional at runtime; install `openai` for live AI responses

## 🚧 Deployment

The app is now live on Streamlit Community Cloud.

- 🌐 **Live App:** https://thebookoftraintodreamland.streamlit.app/
- 🚀 Deployment platform: Streamlit Community Cloud
- 🛠️ Active development is continuing with iterative improvements
- 🔄 Ongoing releases focus on UX, story quality, and system stability

> ✅ **Live now — board the Dreamland journey here:** https://thebookoftraintodreamland.streamlit.app/ ✨

