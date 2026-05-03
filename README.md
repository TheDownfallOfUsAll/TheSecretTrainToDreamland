# The Secret Train to Dreamland

## About this app

The Secret Train to Dreamland is a fantasy storybook web app built with Streamlit. It combines a magical reading experience, a persona-driven AI Fairy chatbot, and user accounts with saved chat history. The app is imagined as being owned by Dreamland guides AC and Nikolai, who offer encouragement, wisdom, and gentle support throughout the experience.

This app lets readers explore:
- A rich Dreamland story featuring Avril, Angel Girl, Crystal Boy, and Philosophy Girl
- A flip-style Storybook with pages 1 to 25
- An AI Fairy Chatbot with alternating persona responses from AC and Nikolai
- User login, registration, profile editing, and saved chat history
- A Settings page to control response style and starting speaker preferences

## First step: install

1. Install Python 3.11 or later.
2. Create a virtual environment and activate it:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install required packages:

```bash
pip install streamlit openai
```

4. Set your OpenAI API key:

```bash
set OPENAI_API_KEY=your_api_key_here
```

5. Run the app:

```bash
streamlit run app.py
```

## Story and features

The app opens into Dreamland with a starry theme and navigation sidebar. As a guest or logged-in user, visitors are invited to enter a world of courage, memory, and magic. The story pages follow Avril on a midnight journey in a floating train, where she meets guides, faces shadows, and learns that bravery grows from small choices.

The AI Fairy Chatbot is a central feature. It responds as AC or Nikolai, offering either action-oriented encouragement or reflective wisdom. Users can choose a response style from Settings, and the app saves conversations to SQLite for each account.

### App sections

- **Home:** Entry page with a Dreamland welcome message
- **Login / Register:** Account sign-in and onboarding
- **Profile:** Edit your full name, bio, and profile image
- **Settings:** Customize chat response style and conversation behavior
- **Characters List:** Meet the main characters and antagonists
- **Storytelling:** A narrative preview with images
- **Table of Story Contents:** Chapter list for the Dreamland adventure
- **Story (Pages 1-25):** A page-by-page storybook reader
- **AI Fairy Chatbot:** Talk with Dreamland guides and save chat history
- **About:** App details, ownership by AC and Nikolai, and guide portraits

## Notes

- The chatbot uses the OpenAI API when `OPENAI_API_KEY` is configured. Without the API key, it falls back to built-in persona replies.
- Chat history is stored locally in `dreamland.db`.
- The app is designed for a magical reading experience with simple, responsive navigation.

Enjoy the journey on The Secret Train to Dreamland!