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

- **Home:** A magical welcome page where Dreamland begins and the story’s tone is introduced.
- **Login / Register:** Create an account or sign in to save chat history and personalize your Dreamland presence.
- **Profile:** Add your full name, write a bio, and select a profile picture to make the adventure feel personal.
- **Settings:** Choose the Fairy chat response style and pick whether AC or Nikolai starts new conversations.
- **Characters List:** Discover the main heroes and villains, including Avril, Angel Girl, Crystal Boy, Philosophy Girl, Ulysses, Helen, Wendell, Jerry, Yeng, the Dark Wizard, the Dark Forest, and Ghost Shadow.
- **Storytelling:** Explore a visual story preview that shows key Dreamland scenes and introduces the adventure.
- **Table of Story Contents:** View chapter titles and the structure for the full Dreamland journey.
- **Story (Pages 1-25):** Read the full Dreamland story page by page, following Avril through each vivid chapter.
- **AI Fairy Chatbot:** Chat with AC and Nikolai, receive supportive guidance, and save your conversations for later.
- **About:** Learn how the app works, meet the Dreamland guides, and discover the ownership lore behind the story.

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