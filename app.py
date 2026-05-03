import streamlit as st
import re
import random
import sqlite3
import hashlib
import os
from datetime import datetime, UTC
from openai import OpenAI

st.set_page_config(
    page_title="The Secret Train to Dreamland",
    page_icon="🚂",
    layout="wide"
)

DB_PATH = "dreamland.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(filename: str) -> str:
    return os.path.join(BASE_DIR, filename)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            bio TEXT DEFAULT '',
            profile_image TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            speaker TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    user_cols = [row["name"] for row in cur.execute("PRAGMA table_info(users)").fetchall()]
    if "full_name" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
    if "bio" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
    if "profile_image" not in user_cols:
        cur.execute("ALTER TABLE users ADD COLUMN profile_image TEXT DEFAULT ''")
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), datetime.now(tz=UTC).isoformat()),
        )
        conn.commit()
        return True, "Registration successful. Please log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def login_user(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, username, full_name, bio, profile_image
        FROM users
        WHERE username = ? AND password_hash = ?
        """,
        (username, hash_password(password)),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def save_chat_message(user_id: int, user_message: str, speaker: str, bot_response: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_history (user_id, user_message, speaker, bot_response, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, user_message, speaker, bot_response, datetime.now(tz=UTC).isoformat()),
    )
    conn.commit()
    conn.close()


def load_chat_history(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_message, speaker, bot_response
        FROM chat_history
        WHERE user_id = ?
        ORDER BY id ASC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [(r["user_message"], r["speaker"], r["bot_response"]) for r in rows]


def clear_chat_history(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_profile(user_id: int, full_name: str, bio: str, profile_image: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET full_name = ?, bio = ?, profile_image = ?
        WHERE id = ?
        """,
        (full_name, bio, profile_image, user_id),
    )
    conn.commit()
    conn.close()


def fetch_user_by_id(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, bio, profile_image FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


init_db()

# ---------------------------------------------------
# FANTASY THEME CSS
# ---------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(180deg, #050816 0%, #120136 45%, #1b1f5e 100%);
        color: white;
    }

    /* STAR BACKGROUND */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(white 1px, transparent 1px),
            radial-gradient(white 1px, transparent 1px),
            radial-gradient(white 2px, transparent 2px);
        background-size: 50px 50px, 100px 100px, 150px 150px;
        opacity: 0.4;
        z-index: -1;
    }

    h1, h2, h3 {
        color: #d7b3ff;
        text-shadow: 0px 0px 15px #7f5cff;
    }

    p, li, div {
        color: white;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090421, #1d1145);
        border-right: 2px solid #7f5cff;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e5d2ff !important;
    }

    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(173, 140, 255, 0.35);
        border-radius: 12px;
        margin-bottom: 8px;
        padding: 10px 12px;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
        background: rgba(132, 94, 247, 0.25);
        border-color: #a688ff;
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(100, 38, 255, 0.7), rgba(39, 138, 255, 0.6));
        border-color: #d7b3ff;
        box-shadow: 0 0 14px rgba(120, 90, 255, 0.55);
    }

    /* STORY CARD */
    .story-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 25px;
        padding: 30px;
        box-shadow: 0 0 25px rgba(127,92,255,0.6);
        backdrop-filter: blur(10px);
        margin-top: 20px;
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #6a00ff, #2d8cff);
        color: white;
        border-radius: 15px;
        border: none;
        padding: 10px 25px;
        font-size: 18px;
        box-shadow: 0 0 15px rgba(127,92,255,0.7);
    }

    .stButton>button:hover {
        transform: scale(1.05);
        transition: 0.3s;
    }

    /* PAGE BOX */
    .page-box {
        background: linear-gradient(145deg, rgba(39,39,90,0.9), rgba(18,1,54,0.9));
        padding: 35px;
        border-radius: 25px;
        border: 2px solid #8d6bff;
        box-shadow: 0 0 30px rgba(110,76,255,0.7);
        min-height: 350px;
    }
    
    /* BOOK TABLE OF CONTENTS STYLE */
    .toc-book {
        background: linear-gradient(145deg, rgba(16, 10, 40, 0.95), rgba(35, 20, 72, 0.95));
        border: 2px solid rgba(182, 154, 255, 0.7);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 0 24px rgba(128, 93, 255, 0.5);
    }

    .toc-item {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 8px 0;
        color: #f1e7ff;
    }

    .toc-dotline {
        flex: 1;
        border-bottom: 1px dashed rgba(218, 199, 255, 0.65);
        height: 1px;
        margin-top: 2px;
    }

    .chat-user-box {
        background: linear-gradient(90deg, rgba(54, 72, 150, 0.9), rgba(83, 126, 255, 0.9));
        border: 1px solid rgba(160, 200, 255, 0.8);
        border-radius: 14px;
        padding: 12px 14px;
        margin: 8px 0 4px 0;
        box-shadow: 0 0 12px rgba(84, 137, 255, 0.45);
    }

    .chat-fairy-box {
        background: linear-gradient(90deg, rgba(93, 45, 180, 0.9), rgba(62, 123, 240, 0.9));
        border: 1px solid rgba(203, 170, 255, 0.85);
        border-radius: 14px;
        padding: 12px 14px;
        margin: 4px 0 14px 0;
        box-shadow: 0 0 14px rgba(145, 102, 255, 0.6);
    }
    .dreamland-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(5, 8, 22, 0.95);
        color: #d7b3ff;
        text-align: center;
        padding: 10px 0;
        border-top: 1px solid rgba(143, 101, 255, 0.5);
        font-size: 14px;
        z-index: 9999;
    }

    .dreamland-footer a {
        color: #92b5ff;
        text-decoration: none;
    }

    .dreamland-footer a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def fairy_reply(speaker: str, text: str, style_mode: str = "Balanced") -> str:
    lower_text = text.strip().lower()
    real_style = style_mode == "Real Guidance"
    balanced_style = style_mode == "Balanced"

    mood_words = {
        "sad": "If your heart feels heavy, breathe slowly and look for one small light to follow.",
        "afraid": "Fear can be a lantern; it shows what matters to you most.",
        "scared": "If your chest tightens, name the feeling and choose one small step forward.",
        "anxious": "Calm comes when you name one worry and decide on one kind answer to it.",
        "happy": "Hold that joy and share it. In Dreamland, joy grows when spoken aloud.",
        "angry": "Set your fire into direction, not destruction. Name the problem, then shape your next step.",
    }
    for mood, response in mood_words.items():
        if mood in lower_text:
            return response

    if any(word in lower_text for word in ["who are you", "your name", "ac", "nikolai"]):
        if real_style:
            return "I am a listening guide grounded in real-world support, here to help you name feelings and choose one clear next step."
        if balanced_style:
            return "I am one guide on the Dreamland Express, speaking both in stories and with real kindness at your side."
        return (
            "I am one guide on the Dreamland Express. AC maps courage, "
            "and Nikolai guards wisdom at the midnight stations."
        )

    if any(word in lower_text for word in ["help", "advice", "what should i do", "should i"]):
        if real_style:
            return "Start with one brave action tonight, then one honest sentence to someone you trust."
        return "Start with one brave action tonight, then one honest sentence to someone you trust."

    if any(word in lower_text for word in ["dream", "nightmare", "sleep", "rest"]):
        if real_style:
            return "Write what you remember in three lines and notice what your mind is trying to tell you."
        return "Write your dream in three lines before sunrise. Hidden meaning appears in small details."

    if any(word in lower_text for word in ["wizard", "shadow", "dark", "scary"]):
        return "Shadows grow when unnamed. Speak the fear directly, and it begins to lose power."

    if any(word in lower_text for word in ["train", "ticket", "journey", "path"]):
        return "Every journey needs a ticket: your ticket is intention. Decide why you travel."

    if real_style:
        return random.choice([
            "It is okay to feel unsure. Focus on one small step you can take right now and keep moving.",
            "Listen to what your body and mind are telling you, then choose a kind way to answer it.",
            "Name one worry, then name one kind thing to say to yourself about it.",
        ])

    if balanced_style:
        return random.choice([
            "This feels important. Blend your real choice with a dreamlike promise, and move toward it step by step.",
            "Both truth and courage matter here. Say what you feel, then choose one gentle action to follow.",
            "Dreamland and the real world both need your honesty. Keep the magic and keep the plan simple.",
        ])

    fallback = {
        "AC": [
            "Courage is not loud. It is the quiet choice to move forward anyway.",
            "Your question carries starlight. Keep asking, and the path will reveal itself.",
            "I hear you. Choose one next action, however small, and begin there.",
        ],
        "Nikolai": [
            "Truth arrives in layers. Be patient with yourself while the full answer forms.",
            "Name what you feel, then name what you need. Clarity follows structure.",
            "Even in Dreamland, wisdom begins with listening before reacting.",
        ],
    }
    return random.choice(fallback.get(speaker, fallback["AC"]))


def openai_fairy_reply(speaker: str, user_text: str, history, style_mode: str = "Balanced"):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None

    persona_map = {
        "AC": (
            "You are AC from Dreamland: warm, brave, action-oriented, concise. "
            "Give practical encouragement and one concrete next step."
        ),
        "Nikolai": (
            "You are Nikolai from Dreamland: thoughtful, philosophical, calm, concise. "
            "Give reflective wisdom and one clear insight."
        ),
    }
    persona = persona_map.get(speaker, persona_map["AC"])

    style_map = {
        "Dreamland Persona": "Stay in-character, imaginative, and gentle.",
        "Balanced": "Mix grounded support with Dreamland persona in a warm and calm way.",
        "Real Guidance": "Use grounded, real-world advice in a gentle way and keep the tone supportive.",
    }
    style_clarifier = style_map.get(style_mode, style_map["Balanced"])

    try:
        client = OpenAI(api_key=api_key)
        recent = history[-6:] if history else []
        convo_lines = []
        for user_msg, spk, bot_msg in recent:
            convo_lines.append(f"User: {user_msg}")
            convo_lines.append(f"{spk}: {bot_msg}")
        convo_text = "\n".join(convo_lines) if convo_lines else "No prior conversation."

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are in a fantasy app chat. Keep responses under 90 words, clean language, "
                        "and stay supportive.\n"
                        + persona
                        + " "
                        + style_clarifier
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Conversation so far:\n{convo_text}\n\n"
                        f"Now respond to the latest user message: {user_text}"
                    ),
                },
            ],
        )
        return response.output_text.strip()
    except Exception:
        return None

# ---------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------

st.sidebar.title("🌌 Dreamland Navigation")

if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.radio(
    "Choose Section",
    [
        "Home",
        "Login",
        "Register",
        "Profile",
        "Settings",
        "Logout",
        "Characters List",
        "Storytelling",
        "Table of Story Contents",
        "Story (Pages 1-25)",
        "AI Fairy Chatbot",
        "About"
    ]
)

# ---------------------------------------------------
# HOME
# ---------------------------------------------------

if menu == "Home":
    st.title("🚂 The Secret Train to Dreamland")
    st.subheader("A Fantasy Storybook Adventure")
    if st.session_state.user:
        st.success(f"Logged in as {st.session_state.user['username']}")
    else:
        st.info("You are browsing as a guest. Log in to use saved AI Fairy chat history.")

    st.markdown(
        """
        <div class="story-card">
        <h2>✨ Welcome to Dreamland ✨</h2>
        <p>
        Enter a magical world of dreams, stars, glowing trains, and unforgettable adventures.
        Follow Avril and her friends as they battle shadows and discover courage.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

elif menu == "Login":
    st.title("🔐 Login")
    st.markdown('<div class="story-card">Sign in to unlock saved Fairy chat history.</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")

    if login_submit:
        if not username.strip() or not password:
            st.error("Please enter both username and password.")
        else:
            user = login_user(username.strip(), password)
            if user:
                st.session_state.user = user
                st.session_state.messages = load_chat_history(user["id"])
                st.session_state.next_speaker = "AC" if len(st.session_state.messages) % 2 == 0 else "Nikolai"
                st.success(f"Welcome back, {user['username']}.")
            else:
                st.error("Invalid username or password.")

elif menu == "Register":
    st.title("📝 Register")
    st.markdown('<div class="story-card">Create an account for persistent Dreamland AI chat.</div>', unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=True):
        new_username = st.text_input("Choose username")
        new_password = st.text_input("Choose password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        register_submit = st.form_submit_button("Register")

    if register_submit:
        if not new_username.strip() or not new_password:
            st.error("Username and password are required.")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            ok, msg = register_user(new_username.strip(), new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# ---------------------------------------------------
# PROFILE / SETTINGS / LOGOUT
# ---------------------------------------------------

elif menu == "Profile":
    st.title("👤 Profile")
    if not st.session_state.user:
        st.warning("Please log in to view and edit your profile.")
        st.stop()

    refreshed_user = fetch_user_by_id(st.session_state.user["id"])
    if refreshed_user:
        st.session_state.user = refreshed_user

    display_name = st.session_state.user.get("full_name") or st.session_state.user["username"]
    st.markdown(f"### {display_name}")
    st.caption(f"Username: @{st.session_state.user['username']}")

    profile_image = st.session_state.user.get("profile_image", "")
    if profile_image and os.path.exists(profile_image):
        st.image(profile_image, caption="Profile Picture", width=220)
    else:
        st.info("No profile picture set.")

    st.markdown("#### Bio")
    st.write(st.session_state.user.get("bio") or "No bio yet.")
    st.markdown("#### Edit Profile")

    local_images = [f for f in os.listdir(BASE_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    image_options = [""] + sorted(local_images)
    current_idx = image_options.index(profile_image) if profile_image in image_options else 0
    with st.form("profile_edit_form", clear_on_submit=False):
        full_name = st.text_input("Full name", value=st.session_state.user.get("full_name", ""))
        bio = st.text_area("Bio", value=st.session_state.user.get("bio", ""), height=120)
        profile_image_choice = st.selectbox(
            "Choose profile image from project files",
            options=image_options,
            index=current_idx,
        )
        save_profile = st.form_submit_button("Save Profile")

    if save_profile:
        update_profile(st.session_state.user["id"], full_name.strip(), bio.strip(), profile_image_choice)
        st.session_state.user = fetch_user_by_id(st.session_state.user["id"])
        st.success("Profile updated.")

elif menu == "Settings":
    st.title("⚙️ Settings")
    if not st.session_state.user:
        st.warning("Please log in to access settings.")
        st.stop()

    st.markdown('<div class="story-card">Account and chat preferences for your Dreamland profile.</div>', unsafe_allow_html=True)
    st.write("Chat history is stored per logged-in account in SQLite.")
    st.write("Use the options below to choose how the AI Fairy responds, manage your story history, and refresh your personal preferences.")

    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(st.session_state.user["id"])

    style_options = ["Dreamland Persona", "Balanced", "Real Guidance"]
    style_index = style_options.index(st.session_state.get("fairy_style", "Balanced"))
    st.session_state.fairy_style = st.radio("AI Fairy response style", style_options, index=style_index)

    start_options = ["Alternating", "AC", "Nikolai"]
    start_index = start_options.index(st.session_state.get("chat_start_preference", "Alternating"))
    st.session_state.chat_start_preference = st.radio("Starting speaker for new chats", start_options, index=start_index)

    st.markdown("#### Chat Preference Summary")
    st.write(f"- Current response style: **{st.session_state.fairy_style}**")
    st.write(f"- Starting speaker: **{st.session_state.chat_start_preference}**")
    st.write(f"- Saved history messages: **{len(st.session_state.messages)}**")

    if st.button("Clear My Saved Chat History"):
        clear_chat_history(st.session_state.user["id"])
        st.session_state.messages = []
        st.session_state.next_speaker = "AC"
        st.success("Saved chat history cleared.")

    if st.button("Reset chat preferences"):
        st.session_state.fairy_style = "Balanced"
        st.session_state.chat_start_preference = "Alternating"
        st.success("Chat preferences reset to default.")

elif menu == "Logout":
    st.title("🚪 Logout")
    if st.session_state.user:
        username = st.session_state.user["username"]
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.next_speaker = "AC"
        st.success(f"{username} has been logged out.")
    else:
        st.info("No user is currently logged in.")

# ---------------------------------------------------
# CHARACTERS
# ---------------------------------------------------

elif menu == "Characters List":
    st.title("🌟 Characters List")

    st.markdown(
        """
        <div class="story-card">

        <h2>👧 Main Character</h2>
        <p><b>Avril</b> — A shy girl chosen by the magical train.</p>

        <h2>🦸 Heroes</h2>
        <p>👼 Angel Girl — Guardian of light and dreams.</p>
        <p>📚 Philosophy Girl — Wise protector of truth.</p>
        <p>💎 Crystal Boy — Hero with crystal powers.</p>

        <h2>👨‍👩‍👧 Family</h2>
        <p>Ulysses — Father of Avril</p>
        <p>Helen — Mother of Avril</p>
        <p>Wendell, Jerry, Yeng — Siblings of Avril</p>

        <h2>🌑 Antagonists</h2>
        <p>🧙 Dark Wizard</p>
        <p>🌲 Dark Forest</p>
        <p>👻 Ghost Shadow</p>

        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# STORYTELLING
# ---------------------------------------------------

elif menu == "Storytelling":
    st.title("📖 Storytelling")

    st.markdown(
        """
        <div class="story-card">
        <p>One magical midnight, Avril hears a glowing train whistle outside her window. The floating train appears beneath the stars and invites children who feel lost.</p>
        <p>When Avril steps aboard, she finds moonlit seats, crystal lanterns, and a conductor who never blinks. He hands her a silver ticket with only one word written on it: <b>Remember</b>. At the next station, Angel Girl joins them with feathered wings lit by constellations. Then comes Crystal Boy, carrying a fractured gem that once protected all of Dreamland. Finally, Philosophy Girl enters quietly, reading from a book whose pages rewrite themselves.</p>
        <p>The train crosses dream-skies where upside-down castles float above rivers of stars. In the Whispering Valley, the group faces Ghost Shadows that steal names from memory. Avril nearly forgets her own voice, but her siblings' laughter echoes from a mirror-lake and brings her back. In the Dark Forest, trees move like giants and paths vanish behind each step; only truth can keep a trail visible, so the friends confess their deepest fears one by one.</p>
        <p>Near the end of the journey, they reach the Dark Wizard's castle. Its clocktower is frozen at midnight, trapping every dream in endless night. While Angel Girl shields the team and Crystal Boy reforms his shattered gem, Philosophy Girl guides Avril through a final test: choosing courage without certainty. Avril sings Helen's lullaby, remembers Ulysses' promise, and the frozen clock begins to move. Dawn spills across Dreamland, dissolving the Final Shadow.</p>
        <p>When Avril returns home, nothing looks exactly the same, because she is not the same. She has learned that bravery is not the absence of fear; it is carrying light through fear, step by step, until morning.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.image(asset_path("avril_angeles.jpg"), caption="Avril — A shy girl chosen by the magical train.", width="stretch")
    st.image(
        asset_path("angelgirl-philosophygirl-crystalboy.jpg"),
        caption="Angel Girl, Philosophy Girl, and Crystal Boy",
        width="stretch",
    )
    col_family1, col_family2 = st.columns(2)
    with col_family1:
        st.image(asset_path("ulysses-helen.jpg"), caption="Ulysses and Helen", width="stretch")
    with col_family2:
        st.image(asset_path("wendell-jerry-yeng.jpg"), caption="Wendell, Jerry, and Yeng", width="stretch")
    st.image(
        asset_path("darkwizard-darkforest-ghostshadow.jpg"),
        caption="Dark Wizard, Dark Forest, and Ghost Shadow",
        width="stretch",
    )
    st.image(asset_path("thesecrettraintodreamlandbook.jpg"), caption="The Secret Train to Dreamland Book", width="stretch")

# ---------------------------------------------------
# TABLE OF CONTENTS
# ---------------------------------------------------

elif menu == "Table of Story Contents":
    st.title("📚 Table of Story Contents")

    contents = [
        "1. The Midnight Whistle",
        "2. The Floating Train",
        "3. Ticket to Dreamland",
        "4. Angel Girl Appears",
        "5. Crystal Boy's Secret",
        "6. The Philosophy Lesson",
        "7. Entering Dreamland",
        "8. Ghost Shadows",
        "9. The Dark Forest",
        "10. Lost Memories",
        "11. Avril's Fear",
        "12. The Broken Clock",
        "13. The Whispering River",
        "14. Battle of Lights",
        "15. The Wizard's Castle",
        "16. The Hidden Door",
        "17. Courage Test",
        "18. Wendell's Voice",
        "19. Jerry and Yeng",
        "20. Helen's Song",
        "21. Ulysses' Promise",
        "22. Crystal Power",
        "23. The Final Shadow",
        "24. Sunrise Returns",
        "25. Home Again"
    ]

    st.markdown('<div class="toc-book">', unsafe_allow_html=True)
    for item in contents:
        chapter_no, chapter_title = item.split(". ", 1)
        st.markdown(
            f"""
            <div class="toc-item">
                <span>📖 Chapter {chapter_no}</span>
                <span class="toc-dotline"></span>
                <span><b>{chapter_title}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# STORY PAGES FLIP BOOK STYLE
# ---------------------------------------------------

elif menu == "Story (Pages 1-25)":

    st.title("📘 Dreamland Storybook")

    pages = {
        1: "At exactly midnight, Avril woke to a whistle that sounded like silver wind through glass. She pushed open her window and saw rails of pale light suspended over the town, curving upward into the sky like a path written by stars. The quiet street below held only the sleeping hum of the world, and for a breath she wondered if the train was a dream. When the whistle came again, it felt as if the night itself were calling her name.",
        2: "A floating train glided out of the dark without touching the ground, wheels turning above mist and stardust. Its windows shone warm gold, and each one reflected a different memory from Avril's childhood that she thought she had lost. The engine breathed like a sleeping giant, and she felt the night become larger than her fear. The air around it smelled faintly of cinnamon and rain.",
        3: "The conductor bowed and offered a silver ticket engraved with her name. On the back, bright ink formed a sentence she could not ignore: 'Board only if you are ready to remember who you are.' Avril held it like a treasure and pressed it to her chest as if it were a key that unlocked more than a door. She stepped forward before doubt could speak.",
        4: "Inside the first carriage, Angel Girl waited beneath a lantern of pure light. Her wings were folded like pages of a sacred book, and her voice was calm enough to quiet the rattling in Avril's heart. She explained that Dreamland did not choose perfect heroes, only honest ones. The doors closed, and the train leapt into the starlit sky.",
        5: "Crystal Boy opened his hands and revealed a fractured crystal heart, still glowing despite its cracks. He said it once protected Dreamland's borders, but each fracture came from fear left unnamed. If the crystal shattered completely, shadows would pour into every sleeping mind. Avril touched the crystal and felt both cold terror and stubborn hope.",
        6: "In the library carriage, Philosophy Girl unfolded a map made of moving sentences. Paths appeared only when travelers spoke the truth, and false words turned bridges into mist. She told Avril that direction was not a place but a practice. Avril watched the letters rearrange themselves and understood the journey would test her voice as much as her courage.",
        7: "The train crossed a sea of clouds where upside-down towers floated like chandeliers. Comets passed so close they painted violet and blue light across Avril's hands and sleeves. Far below, rivers looked like silver threads stitched through darkness. She felt wonder take the seat where worry had been sitting for years.",
        8: "At the first tunnel gate, Ghost Shadows rose from the walls and whispered in familiar voices: old judgments, old embarrassments, old failures. The words struck like tiny stones against her confidence. Angel Girl raised her lantern, and the whispers thinned, but they did not disappear. Avril learned that bravery was not silence around fear, but movement through it.",
        9: "In the Dark Forest, trees bent across the trail and roots moved like sleeping snakes disturbed by moonlight. Every few steps the path disappeared behind them, forcing the travelers to trust what they could not see. Philosophy Girl said only spoken truth could anchor the road. One by one they named a fear, and the ground steadied beneath their feet.",
        10: "The Hall of Mirrors held drifting memories like smoke trapped in glass. Avril saw the day she stayed quiet when she wanted to sing, the day she laughed to hide her hurt, the day she let someone else define her. The mirrors did not accuse her; they returned each moment as instruction. She left the hall lighter, not because the past changed, but because she finally faced it.",
        11: "When asked her deepest fear, Avril admitted she was afraid of being ordinary and unseen forever. Her voice shook as the words left her mouth, and for a second she wanted to pull them back. Philosophy Girl answered, 'Quiet hearts often carry the longest-burning light.' The chamber brightened, as though truth itself had opened a hidden window.",
        12: "Above the valley stood a celestial clocktower, its frozen hands pinning Dreamland to endless midnight. Each silent gear looked like a promise interrupted. Crystal Boy explained that sunrise could not return until the clock remembered motion. Avril stared up at the still face and felt time waiting for someone brave enough to touch it.",
        13: "At the Whispering River, water spoke in fragments of lullabies and unfinished vows. Among the voices she heard Ulysses, steady and warm: 'Courage can be inherited, but it must be chosen each day.' The sentence circled her like a protective thread. She repeated it until it sounded less like memory and more like her own decision.",
        14: "Ghost Shadows attacked again, this time in waves that filled the bridge with black wind and broken echoes. Angel Girl held the front while Crystal Boy sealed cracks in the rail with sparks from his gem. Avril stopped waiting to feel ready and moved anyway, one step at a time. Action became her answer before certainty arrived.",
        15: "The Dark Wizard's castle rose from stone and storm, a silhouette of jagged towers against a moonless sky. Light touched the walls and slid away as if refused. The gate opened only when Crystal Boy pressed his cracked gem to an eclipse seal. Inside, the air smelled of rain, iron, and old regret.",
        16: "Corridors looped in impossible circles, returning them to the same door with different shadows under it. Then silver words appeared on the wall, forming Nikolai's riddle: 'What opens when named, and closes when denied?' Avril whispered, 'Fear,' and a hidden stair revealed itself behind a black tapestry. At the bottom waited a chamber where nightmares were forged into chains.",
        17: "Each traveler faced a private trial designed to tempt, not terrify. Avril was offered safety without risk, praise without effort, and a future where she could never fail because she would never try. The illusion was beautiful and empty. She refused it, and the false world cracked like thin ice beneath sunlight.",
        18: "Through the fog she heard Wendell's laughter, bright as a bell, cutting through panic with ordinary love. She remembered small moments from home: shared meals, arguments, forgiveness, and hands reaching for each other without ceremony. The memory guided her across a crumbling walkway one careful step at a time. She realized home had never been behind her; it was traveling with her.",
        19: "Jerry and Yeng appeared beside her as glowing memory-figures, offering short, certain words: 'Keep going.' 'You know this path.' Their presence did not remove danger, but it removed loneliness. Panic turned into focus, and cracks spread across the chamber walls. The shadow-spell feeding on hesitation began to starve.",
        20: "Helen's lullaby moved through the castle stones like warm wind through winter branches. Soft but relentless, the melody reached locked rooms and frozen gears alike. Shadow-chains around the clockwork core loosened link by link. Avril sang with it, barely above a whisper, and felt the tower listening.",
        21: "Then came Ulysses' promise, clear as a hand on her shoulder: 'You are never alone, even when you lead.' Avril repeated it until her breathing steadied and her steps matched the rhythm of the sleeping clock. Leadership stopped feeling like isolation and became a form of care. The final tower door opened before she touched it.",
        22: "Crystal Boy reunited the fractured gem, and light burst through the castle in geometric waves. Constellations spilled across the floor, mapping a route to the summit like a sky laid flat for travelers. Angel Girl held back the last shadows while Philosophy Girl translated the star-path. Avril followed the glowing pattern without looking away.",
        23: "At the summit, the Final Shadow rose like a storm wearing a human shape. It repeated every doubt Avril had ever believed and offered her one last chance to surrender. Instead of arguing, she placed both hands on the frozen clock hand and pushed with everything left in her. The shadow screamed as time began to move.",
        24: "The tower shook, gears thundered, and dawn split the horizon open in gold. Shadows unraveled into harmless smoke and scattered into the high air. The Dark Wizard's power collapsed with the night, revealing only fear where cruelty once stood. Dreamland exhaled, and birdsong replaced the long silence.",
        25: "Before sunrise in the waking world, Avril returned home with the silver ticket still warm in her pocket. The street looked the same, her room looked the same, and yet everything had changed because she had changed. She understood at last that bravery is built from repeated choices, not sudden miracles. She smiled at the morning light and knew the story would continue, page after page, each time she chose to begin again."
    }

    if "page" not in st.session_state:
        st.session_state.page = 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅ Previous"):
            if st.session_state.page > 1:
                st.session_state.page -= 1

    with col3:
        if st.button("Next ➡"):
            if st.session_state.page < 25:
                st.session_state.page += 1

    st.session_state.page = st.slider(
        "Jump to page",
        min_value=1,
        max_value=25,
        value=st.session_state.page,
    )

    current_page = st.session_state.page

    st.markdown(
        f"""
        <div class="page-box">
        <h1>📖 Page {current_page}</h1>
        <p style="font-size:24px; line-height:2;">
        {pages[current_page]}
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# AI FAIRY CHATBOT
# ---------------------------------------------------

elif menu == "AI Fairy Chatbot":

    st.title("🧚 AI Fairy Chatbot")

    st.markdown(
        """
        <div class="story-card">
        Talk with AC and Nikolai about Dreamland.
        Swearing and inappropriate language are blocked.
        </div>
        """,
        unsafe_allow_html=True
    )

    banned_words = ["badword", "curse", "swear"]

    if not st.session_state.user:
        st.warning("Please log in first. AI Fairy chat history is saved per account.")
        st.stop()

    if "fairy_style" not in st.session_state:
        st.session_state.fairy_style = "Balanced"
    if "chat_start_preference" not in st.session_state:
        st.session_state.chat_start_preference = "Alternating"
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(st.session_state.user["id"])
    if "next_speaker" not in st.session_state:
        if st.session_state.chat_start_preference == "AC":
            st.session_state.next_speaker = "AC"
        elif st.session_state.chat_start_preference == "Nikolai":
            st.session_state.next_speaker = "Nikolai"
        else:
            st.session_state.next_speaker = "AC" if len(st.session_state.messages) % 2 == 0 else "Nikolai"

    with st.form("fairy_chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask the Fairy AI")
        send_chat = st.form_submit_button("Send")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.next_speaker = "AC"
        clear_chat_history(st.session_state.user["id"])

    if send_chat and user_input:
        normalized_input = user_input.lower()
        banned_pattern = r"\b(" + "|".join(map(re.escape, banned_words)) + r")\b"
        if re.search(banned_pattern, normalized_input):
            speaker = st.session_state.next_speaker
            response = "⚠️ Dreamland magic asks you to use respectful words."
        else:
            speaker = st.session_state.next_speaker
            response = openai_fairy_reply(
                speaker,
                user_input,
                st.session_state.messages,
                style_mode=st.session_state.fairy_style,
            )
            if not response:
                response = fairy_reply(speaker, user_input, style_mode=st.session_state.fairy_style)
            if st.session_state.chat_start_preference == "Alternating":
                st.session_state.next_speaker = "Nikolai" if speaker == "AC" else "AC"
            else:
                st.session_state.next_speaker = speaker

        st.session_state.messages.append((user_input, speaker, response))
        save_chat_message(st.session_state.user["id"], user_input, speaker, response)

    for msg, speaker, res in st.session_state.messages:
        st.markdown(
            f'<div class="chat-user-box"><b>🧒 You:</b> {msg}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="chat-fairy-box"><b>🧚 {speaker}:</b> {res}</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------
# ABOUT
# ---------------------------------------------------

elif menu == "About":

    st.title("ℹ️ About")

    st.markdown(
        """
        <div class="story-card">

        <h2>🚂 The Secret Train to Dreamland</h2>

        <p>
        A magical storytelling experience built in Streamlit, designed to inspire readers through dreamlike adventures, emotional growth, and gentle guidance.
        </p>

        <p>
        The app is guided by the Dreamland spirits AC and Nikolai, who shape the narrative, the AI Fairy chatbot, and the supportive world around Avril.
        This story app is imagined as being owned by AC and Nikolai, who invite you to explore courage, truth, and kindness.
        </p>

        <h2>🌌 Features</h2>

        <ul>
            <li>Fantasy Galaxy Theme</li>
            <li>Flip-Page Storybook</li>
            <li>AI Fairy Chatbot with AC and Nikolai</li>
            <li>Dreamland Navigation</li>
            <li>Personalized account, profile, and chat history</li>
        </ul>

        <p>
        Built with imagination for readers who love stars, mystery, and magical journeys. Owned and guided by AC and Nikolai, this app blends storybook wonder with gentle, real-world support.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Meet the Dreamland Guides")
    col_ac, col_nikolai = st.columns(2)
    with col_ac:
        if os.path.exists(asset_path("ac-b.jpg")):
            st.image(asset_path("ac-b.jpg"), caption="AC — The courageous guide of Dreamland.", width="stretch")
        else:
            st.info("Image 'ac-b.jpg' is not available.")
        st.markdown(
            """
            <p><b>AC</b> brings practical encouragement and bold but gentle wisdom. AC helps you turn feeling into action.</p>
            """,
            unsafe_allow_html=True,
        )
    with col_nikolai:
        if os.path.exists(asset_path("nikolai-j.jpg")):
            st.image(asset_path("nikolai-j.jpg"), caption="Nikolai — The calm, thoughtful guide of Dreamland.", width="stretch")
        else:
            st.info("Image 'nikolai-j.jpg' is not available.")
        st.markdown(
            """
            <p><b>Nikolai</b> offers reflective wisdom, calm perspective, and quiet strength. Nikolai helps you understand what matters most.</p>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="dreamland-footer">
        <span>Owned by AC & Nikolai — Dreamland storytelling, friendly guidance, and magical support.</span>
    </div>
    """,
    unsafe_allow_html=True,
)
