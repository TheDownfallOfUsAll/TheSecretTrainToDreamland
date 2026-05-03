# 🚂 The Secret Train to Dreamland

## ✨ About this app

Welcome to **The Secret Train to Dreamland** — a magical fantasy storybook app built with **Streamlit**. This dreamy experience blends:

- immersive storybook pages
- persona-based AI chat with **AC** and **Nikolai**
- user accounts, profile editing, and persistent chat history
- playful fantasy design and responsive navigation

The app is imagined as being created and owned by the Dreamland guides **AC** and **Nikolai**, who invite users to explore courage, truth, kindness, and quiet wisdom.

## 🧭 What you can explore

- A rich Dreamland story starring **Avril**, **Angel Girl**, **Crystal Boy**, and **Philosophy Girl**
- A page-turning Storybook with **25 story pages**
- AI Fairy Chatbot with alternating guidance from **AC** and **Nikolai**
- Login, registration, and personal profile support
- Chat preferences for style and speaker choice

## 🚀 First step: install

1. Install **Python 3.11** or later.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install streamlit openai
```

4. Add your OpenAI API key:

```bash
set OPENAI_API_KEY=your_api_key_here
```

5. Start the app:

```bash
streamlit run app.py
```

## 📖 Story and features

This app brings Dreamland to life with a starry atmosphere, enchanted train imagery, and a gentle narrative voice. Visitors can travel through the story, meet characters, and interact with the AI Fairy chatbot to receive either practical encouragement or reflective insight.

AC offers action-focused guidance, while Nikolai shares calm, thoughtful wisdom. The chatbot can use the OpenAI API when available and falls back to built-in persona responses if the API key is missing.

### App sections

- **Home:** Magical welcome page with Dreamland introduction
- **Login / Register:** Create an account or sign in
- **Profile:** Add name, bio, and profile picture
- **Settings:** Choose chat style and starting speaker
- **Characters List:** Discover the main heroes and villains
- **Storytelling:** Explore a visual story preview
- **Table of Story Contents:** View chapter titles and structure
- **Story (Pages 1-25):** Read the full Dreamland story page by page
- **AI Fairy Chatbot:** Chat with AC and Nikolai and save your conversations
- **About:** Learn how the app works and meet the Dreamland guides

## 📝 Notes

- The AI Fairy chat uses the OpenAI API if `OPENAI_API_KEY` is configured.
- If no API key is set, the app still responds using built-in AC/Nikolai persona replies.
- Chat history is saved locally in `dreamland.db`.
- The app focuses on a magical reading experience with friendly and simple navigation.

## 🚧 Deployment

This app is still **under development** and being improved continuously.

- A public web link will be shared soon 🎉
- For now, run it locally using the setup above
- Future updates may include design polish, extra story content, and better mobile support

> Link coming soon — stay tuned for the Dreamland launch! 🌟

Enjoy the journey on The Secret Train to Dreamland! 🚆✨