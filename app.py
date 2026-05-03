import streamlit as st
import re
import random
import sqlite3
import hashlib
import os
from datetime import datetime, UTC
try:
    from openai import OpenAI
except ModuleNotFoundError:
    OpenAI = None

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

    .home-hero {
        background: linear-gradient(135deg, rgba(73, 48, 150, 0.65), rgba(26, 98, 186, 0.55));
        border: 1px solid rgba(212, 192, 255, 0.6);
        border-radius: 24px;
        padding: 26px;
        box-shadow: 0 0 24px rgba(114, 86, 255, 0.45);
        margin-bottom: 16px;
    }

    .home-pill {
        display: inline-block;
        margin: 6px 8px 0 0;
        padding: 7px 12px;
        border-radius: 999px;
        border: 1px solid rgba(220, 203, 255, 0.7);
        background: rgba(255, 255, 255, 0.1);
        color: #f5ecff;
        font-size: 0.92rem;
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
    if OpenAI is None:
        return None

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
        <div class="home-hero">
            <h2>✨ Welcome to Dreamland ✨</h2>
            <p>
            Step into a magical world of stars, glowing rails, and brave choices.
            Follow Avril and her companions through 25 long-read chapters filled with wonder,
            fear, memory, and courage.
            </p>
            <span class="home-pill">📖 25 Story Pages</span>
            <span class="home-pill">🧚 AC & Nikolai Chat</span>
            <span class="home-pill">🔐 Login + Profile</span>
            <span class="home-pill">💾 SQLite Saved History</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Story Chapters", "25")
    with col_b:
        st.metric("AI Guides", "2", "AC • Nikolai")
    with col_c:
        st.metric("Chat Storage", "Per User", "SQLite")

    st.markdown(
        """
        <div class="story-card">
            <h3>🌌 Start Here</h3>
            <p>
            New reader: open <b>Table of Story Contents</b> then continue with <b>Story (Pages 1-25)</b>.<br>
            Returning reader: log in to continue your saved AI Fairy conversations and profile settings.<br>
            Want guidance now: open <b>AI Fairy Chatbot</b> and ask AC or Nikolai anything.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        asset_path("thesecrettraintodreamlandbook.jpg"),
        caption="The book that inspired the magical journey into Dreamland.",
        width="stretch",
    )

elif menu == "Login":
    st.title("🔐 Login")
    st.markdown('<div class="story-card">Sign in to unlock saved Fairy chat history.</div>', unsafe_allow_html=True)
    if st.session_state.user:
        st.success(f"You are currently logged in as {st.session_state.user['username']}.")

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
    st.caption("Tip: use a memorable username and a password with at least 6 characters.")

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
    st.markdown("#### Account Snapshot")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.metric("Saved Messages", len(load_chat_history(st.session_state.user["id"])))
    with col_p2:
        st.metric("Profile Image", "Set" if profile_image else "Not Set")
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

    st.markdown("#### Account Maintenance")
    st.caption("Use logout to switch account quickly and safely from the sidebar navigation.")

elif menu == "Logout":
    st.title("🚪 Logout")
    if st.session_state.user:
        username = st.session_state.user["username"]
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.next_speaker = "AC"
        st.success(f"{username} has been logged out.")
        st.info("You can log in again anytime from the Login tab.")
    else:
        st.info("No user is currently logged in.")

# ---------------------------------------------------
# CHARACTERS
# ---------------------------------------------------

elif menu == "Characters List":
    st.title("🌟 Characters List")
    st.caption("Meet the heroes, family, and shadows shaping Avril's Dreamland journey.")

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

    st.markdown("### Character Portraits")
    st.image(asset_path("avril_angeles.jpg"), caption="Avril — A shy girl chosen by the magical train.", width="stretch")
    st.image(
        asset_path("angelgirl-philosophygirl-crystalboy.jpg"),
        caption="Angel Girl, Philosophy Girl, and Crystal Boy, united to protect Dreamland.",
        width="stretch",
    )
    col_family1, col_family2 = st.columns(2)
    with col_family1:
        st.image(asset_path("ulysses-helen.jpg"), caption="Ulysses and Helen — Avril's parents.", width="stretch")
    with col_family2:
        st.image(asset_path("wendell-jerry-yeng.jpg"), caption="Wendell, Jerry, and Yeng — Avril's siblings.", width="stretch")
    st.image(
        asset_path("darkwizard-darkforest-ghostshadow.jpg"),
        caption="Dark Wizard, Dark Forest, and Ghost Shadow — the forces Avril must face.",
        width="stretch",
    )

# ---------------------------------------------------
# STORYTELLING
# ---------------------------------------------------

elif menu == "Storytelling":
    st.title("📖 Storytelling")
    st.caption("A cinematic preview of the full Dreamland arc before you open the complete storybook.")

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

# ---------------------------------------------------
# TABLE OF CONTENTS
# ---------------------------------------------------

elif menu == "Table of Story Contents":
    st.title("📚 Table of Story Contents")
    st.caption("Use this chapter guide, then switch to Story (Pages 1-25) and jump to any page.")

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
    st.info("Navigation tip: open 'Story (Pages 1-25)' and use the slider to jump directly to a chapter page.")

# ---------------------------------------------------
# STORY PAGES FLIP BOOK STYLE
# ---------------------------------------------------

elif menu == "Story (Pages 1-25)":

    st.title("📘 Dreamland Storybook")
    st.caption("Long-read mode: each page is written as a full narrative paragraph for immersive reading.")

    pages = {
        1: "At exactly midnight, Avril woke to a whistle that sounded like silver wind through glass, soft at first and then clear enough to pull sleep from her eyes. She pushed open her window and saw rails of pale light suspended above the town, curving upward into the sky like a path written by stars. The quiet street below held only the distant hum of electricity and the hush of sleeping houses, yet the air around her window trembled as if waiting for an answer. She stood in her nightclothes, heart pounding, wondering whether the sight was a dream sent by an overfull imagination. When the whistle came again, lower and warmer, it felt as if the night itself had learned her name and was calling her to step beyond everything familiar.",
        2: "A floating train glided out of darkness without touching the ground, its wheels turning above mist and stardust as if gravity had made an exception. Its windows shone warm gold, and each one reflected a different memory from Avril's childhood: a paper kite, a birthday candle, her mother's hands braiding her hair. The engine breathed like a sleeping giant, releasing tiny clouds that smelled faintly of cinnamon, rain, and old books. Lanterns along the roofline flickered in shades of blue and violet, painting the walls of nearby houses with moving color. As the train slowed beneath her window, Avril felt something impossible happen inside her: the night became larger than fear.",
        3: "The conductor stepped down and bowed with formal grace, his coat lined with constellations that shifted each time he moved. He offered a silver ticket engraved with Avril's full name in letters so fine they looked etched by moonlight. On the back, bright ink formed a sentence she could not ignore: 'Board only if you are ready to remember who you are.' Avril held it like a treasure and pressed it to her chest as though it were a key that unlocked more than a door. A hundred practical thoughts tried to stop her, but none were stronger than the quiet certainty rising in her bones. Before doubt could gather its voice, she placed one foot on the glowing step.",
        4: "Inside the first carriage, Angel Girl waited beneath a lantern of pure light that made shadows retreat to the corners. Her wings were folded like pages of a sacred book, and her calm voice settled the rattling in Avril's chest. She explained that Dreamland did not choose perfect heroes, only honest ones willing to name what they feared. Velvet seats lined the carriage, and crystal bells above each window chimed whenever the train changed direction. As the doors closed and the cabin warmed, Avril watched the town fall away below her like a folded map. Then, with a gentle lurch, the train leapt into the starlit sky.",
        5: "In the second carriage, Crystal Boy opened his hands and revealed a fractured crystal heart, still glowing despite the fine cracks running through it like frozen lightning. He said it once protected Dreamland's borders, but each fracture was born from fear left unnamed by those who carried it too long. If the crystal shattered completely, shadows would pour into every sleeping mind and turn dreams into cages. Avril reached out and touched the edge; the surface was cold, yet beneath it she felt a pulse like stubborn hope refusing to die. Crystal Boy smiled sadly and said the heart could heal, but only if courage was chosen again and again. For the first time, Avril understood that bravery might be less a feeling and more a discipline.",
        6: "In the library carriage, Philosophy Girl unfolded a map made of moving sentences that slid across parchment like fish through water. Paths appeared only when travelers spoke the truth, while false words made bridges fade into mist. She traced a route with her finger and told Avril that direction was not a place but a practice, a way of choosing with clarity when fear offered shortcuts. Shelves around them held books without titles, and each spine glowed when Avril looked directly at it, as if waiting to be opened at the right moment. She watched letters rearrange themselves in response to their voices and realized the journey would test her speech as much as her strength. Every answer she gave would shape the road ahead.",
        7: "The train crossed a sea of clouds where upside-down towers floated like chandeliers suspended from invisible ceilings. Comets passed so close they painted violet and blue light across Avril's sleeves, leaving brief sparks on the window glass. Far below, rivers looked like silver threads stitched through darkness, and mountain ranges resembled folded blankets laid over sleeping giants. Children in distant cloud-villages waved from balconies made of crystal, their lanterns bobbing like fireflies. Avril pressed her palm to the window and felt wonder quietly replace the old seat where worry had lived for years. She realized she was no longer simply being carried by the train; she was being changed by it.",
        8: "At the first tunnel gate, Ghost Shadows rose from the walls and whispered in familiar voices: old judgments, old embarrassments, old failures she had replayed in private. Their words struck like tiny stones against her confidence, stinging not because they were true, but because they were known. Angel Girl raised her lantern, and the whispers thinned into threads, though they did not vanish completely. Crystal Boy told her that fear rarely disappears on command; it weakens when faced in motion. Avril kept walking, each step a small act of refusal against the chorus behind her. There, between trembling and progress, she learned that bravery is not silence around fear, but movement through it.",
        9: "In the Dark Forest, trees bent across the trail and roots moved like sleeping snakes disturbed by moonlight, reshaping the ground whenever someone hesitated. Every few steps the path dissolved behind them, forcing the travelers to trust what they could not see and remember what they had promised. Philosophy Girl said only spoken truth could anchor the road, so each traveler named one fear aloud. As they confessed, pale markers rose from the earth like glowing milestones, and the wind lost some of its bite. Avril admitted she feared disappointing the people she loved, and the nearest tree slowly lifted its branches to let them pass. By the time they reached the forest edge, the path behind them had become solid stone.",
        10: "The Hall of Mirrors held drifting memories like smoke trapped in glass, each pane reflecting a version of Avril she had forgotten or avoided. She saw the day she stayed quiet when she wanted to sing, the day she laughed to hide hurt, the day she let someone else define her limits. The mirrors did not accuse; they returned each moment as instruction, offering a second perspective rather than a second chance. Some reflections were painful, but none were pointless, and each one asked the same question: what will you do differently now? Avril touched the cold frame of the final mirror and felt the smoke clear. She left the hall lighter, not because the past changed, but because she chose to carry it with understanding instead of shame.",
        11: "When asked her deepest fear, Avril admitted she was afraid of being ordinary and unseen forever, the kind of fear that grows quietly behind polite smiles. Her voice shook as the words left her mouth, and for a second she wanted to gather them back before anyone could hear. Philosophy Girl answered, 'Quiet hearts often carry the longest-burning light,' then asked her to stand still and breathe. As Avril inhaled, the chamber brightened around her, and hidden windows opened in the stone walls where no windows had existed before. A soft dawn-colored glow crossed the floor and touched her shoes like a blessing. In that light, her confession stopped feeling like weakness and started feeling like direction.",
        12: "Above the valley stood a celestial clocktower, its frozen hands pinning Dreamland to endless midnight while gears slept behind cracked bronze faces. Each silent tooth and wheel looked like a promise interrupted halfway through fulfillment. Crystal Boy explained that sunrise could not return until the clock remembered motion and consented to time again. Storm clouds circled the tower but never struck it, as if even thunder waited for permission. Avril stared up at the still face and felt time itself watching her, patient and heavy. She understood that touching the clock would mean touching everything she had avoided.",
        13: "At the Whispering River, water spoke in fragments of lullabies, unfinished vows, and names carried from distant homes. Among the voices Avril heard Ulysses, steady and warm: 'Courage can be inherited, but it must be chosen each day.' The sentence circled her like a protective thread, wrapping around her thoughts whenever panic tried to rise. She knelt, cupped the river water, and saw brief reflections of her family smiling as if from the far side of sleep. Repeating the words, she felt them shift from memory into commitment. By the time she stood, her knees were wet and her resolve was clearer.",
        14: "Ghost Shadows attacked again, this time in waves that filled the bridge with black wind, broken echoes, and faces made of smoke. Angel Girl held the front line while Crystal Boy sealed cracks in the rail with sparks from his gem, each spark hissing like rain on stone. Philosophy Girl shouted directions over the storm, but the noise swallowed half the words. Avril stopped waiting to feel ready and moved anyway, one hand on the rail, one step at a time through trembling legs. She found that action could arrive before confidence and still be enough. By the bridge's end, fear had not vanished, but it no longer led.",
        15: "The Dark Wizard's castle rose from stone and storm, a silhouette of jagged towers against a moonless sky that seemed to drink nearby light. Every wall was etched with symbols of forgotten promises, and the gates stood closed like iron jaws. Light touched the surface and slid away as if refused, leaving only cold reflections in puddles at their feet. The gate opened only when Crystal Boy pressed his cracked gem to an eclipse seal hidden under frost. Inside, the corridors smelled of rain, iron, extinguished candles, and old regret. Avril crossed the threshold knowing the hardest pages of the journey had begun.",
        16: "Corridors looped in impossible circles, returning the travelers to the same door with different shadows beneath it, as if the castle were testing their attention. Then silver words appeared on a black wall, forming Nikolai's riddle: 'What opens when named, and closes when denied?' The letters shimmered and pulsed with each heartbeat until Avril whispered, 'Fear.' Immediately, a hidden stair unfolded from behind a tapestry dark as starless water. They descended past whispering chains and murals of dreams turned into cages. At the bottom waited a chamber where nightmares were forged, each one glowing like hot metal before being hammered into shape.",
        17: "Each traveler faced a private trial designed to tempt rather than terrify, because temptation can chain a person more gently than terror. Avril was offered safety without risk, praise without effort, and a future where she could never fail because she would never try. The illusion looked beautiful: a quiet house, polite applause, an easy life that asked nothing costly. Yet beneath the surface she sensed a deep emptiness, like music played with no heart behind it. She refused the offer, and the false world cracked like thin ice under sunlight. When it shattered, she stood in darkness again, but this time with clearer eyes.",
        18: "Through the fog she heard Wendell's laughter, bright as a bell, cutting through panic with the ordinary grace of being known. She remembered small moments from home: shared meals, arguments followed by forgiveness, hands reaching for each other without ceremony. Those memories did not remove danger, but they reminded her what she was fighting to protect. A narrow walkway crumbled beneath her feet, and she crossed it one careful step at a time, guided by that familiar sound. At the far side, she looked back and saw nothing but mist where the path had been. Home, she realized, had never been behind her; it was traveling within her.",
        19: "Jerry and Yeng appeared beside her as glowing memory-figures, not fully solid, yet strong enough to steady her breathing. They offered short, certain words: 'Keep going.' 'You know this path.' Their presence did not erase danger, but it erased loneliness, and that changed everything. Panic narrowed into focus, and she began to notice patterns in the chamber walls where before there had only been chaos. Cracks spread through the stone as the shadow-spell feeding on hesitation began to starve. For the first time in the tower, silence sounded possible.",
        20: "Helen's lullaby moved through the castle stones like warm wind through winter branches, soft yet relentless, finding every hidden seam. The melody reached locked rooms and frozen gears alike, carrying tenderness into places built for fear. Shadow-chains around the clockwork core loosened link by link, each release ringing like a distant bell. Avril sang with it, barely above a whisper at first, then steadier as the echoes joined her. She felt the tower listening, not as an enemy, but as a long-suffering creature waiting to remember kindness. Even the air seemed to brighten with each note.",
        21: "Then came Ulysses' promise, clear as a hand on her shoulder: 'You are never alone, even when you lead.' Avril repeated the words until her breathing steadied and her steps matched the rhythm of the sleeping clock beneath her feet. Leadership stopped feeling like isolation and became a form of care, an agreement to move first so others could follow safely. She climbed the final stair with her heart still afraid but no longer divided. When she reached the top landing, the final tower door opened before she touched it. Beyond it waited the mechanism that held back dawn.",
        22: "Crystal Boy reunited the fractured gem, and light burst through the castle in geometric waves that ran along floors, walls, and ceilings like living constellations. Stars spilled across the stone, mapping a route to the summit like a sky laid flat for travelers who had forgotten how to look up. Angel Girl held back the last shadows while Philosophy Girl translated the star-path in a voice both urgent and calm. Avril followed the glowing pattern without looking away, even when echoes tried to pull her attention sideways. Each step activated another ring of symbols until the entire corridor shone like a promise being rewritten. By the final archway, the gem's light had become almost sunrise-bright.",
        23: "At the summit, the Final Shadow rose like a storm wearing human shape, tall enough to touch the ceiling and cold enough to fog the air. It repeated every doubt Avril had ever believed and offered her one last chance to surrender in exchange for painless stillness. Instead of arguing with it, she placed both hands on the frozen clock hand and pushed with everything left in her body. The metal resisted, then groaned, then moved a fraction that felt like a continent. The shadow screamed as time began to flow, its edges unraveling into smoke. Avril kept pushing until the minute hand crossed the first mark.",
        24: "The tower shook, gears thundered, and dawn split the horizon open in gold so bright it painted every cloud with fire. Shadows unraveled into harmless smoke and scattered into the high air, where wind broke them apart like old ash. The Dark Wizard's power collapsed with the night, revealing only fear where cruelty once stood; without darkness to feed it, command turned to emptiness. Bells across Dreamland rang in staggered waves as villages and forests welcomed morning. Birdsong poured through broken windows and settled on the rails outside like blessings. Dreamland exhaled, and for the first time the silence sounded restful.",
        25: "Before sunrise in the waking world, Avril returned home with the silver ticket still warm in her pocket and starlight fading from her sleeves. The street looked the same, her room looked the same, and yet everything had changed because she had changed in ways no mirror could fully show. She sat at her window until dawn, listening to ordinary sounds begin again: a bicycle chain, a kettle whistle, a neighbor opening a gate. None of it felt small anymore. She understood at last that bravery is built from repeated choices, not sudden miracles, and that courage can be practiced in kitchens and classrooms as surely as in castles. Smiling at the morning light, she knew the story would continue, page after page, each time she chose to begin again."
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
    st.progress(current_page / 25, text=f"Reading progress: Page {current_page} of 25")

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
    st.caption("AC and Nikolai alternate by design. Response style and starting speaker can be customized in Settings.")

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
    st.caption(f"Conversation turns saved: {len(st.session_state.messages)}")

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
    st.markdown(
        """
        <div class="story-card">
        <h3>🛠 Platform Highlights</h3>
        <p>
        This app includes authentication, profile management, SQLite persistence,
        long-form story navigation, and OpenAI-powered fairy chat with local fallback.
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
