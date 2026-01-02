import streamlit as st
import google.generativeai as genai
import sqlite3

# --- 1. SETUP & SECRETS ---
st.set_page_config(page_title="Habibi Dubai Guide", layout="wide", page_icon="🌴")

# This pulls the key from the "vault" you just filled
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("Missing API Key! Please check the Streamlit Secrets tab.")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. DATABASE SETUP ---
def init_db():
    # 'check_same_thread=False' is required for Streamlit
    conn = sqlite3.connect("habibi.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS chat (sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn

conn = init_db()

# --- 3. UI LAYOUT ---
st.title("Habibi Dubai Guide 🌴")
st.markdown("Your AI-powered companion for exploring Dubai.")

tab1, tab2, tab3 = st.tabs(["🈯 Translator", "📍 Explore Dubai", "💬 Chat with Habibi"])

# --- TAB 1: TRANSLATOR ---
with tab1:
    st.header("English to Arabic")
    text_to_translate = st.text_input("Enter a word or phrase (e.g., Hello, Where is the mall?):")
    
    if st.button("Translate Now"):
        if text_to_translate:
            with st.spinner("Translating..."):
                prompt = f"Translate '{text_to_translate}' to Arabic. Provide: 1. Arabic Script, 2. English Phonetics, 3. A brief usage tip."
                try:
                    res = model.generate_content(prompt)
                    st.success(res.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.warning("Please enter some text first.")

# --- TAB 2: EXPLORE ---
with tab2:
    st.header("Top Dubai Recommendations")
    category = st.selectbox("Choose a category:", ["Top Attractions", "Luxury Hotels", "Budget Eats", "Hidden Gems"])
    
    if st.button("Get Recommendations"):
        with st.spinner(f"Fetching {category}..."):
            prompt = f"List 3 {category} in Dubai. For each, give the name, estimated price in AED, and one 'local' tip."
            try:
                res = model.generate_content(prompt)
                st.info(res.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

# --- TAB 3: AI CHAT ---
with tab3:
    st.header("Chat with Habibi AI")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything about Dubai..."):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Habibi is typing..."):
                try:
                    res = model.generate_content(f"You are a helpful Dubai travel guide. User asks: {prompt}")
                    response_text = res.text
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Save to local SQLite database
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO chat (sender, message) VALUES (?,?)", ("User", prompt))
                    cursor.execute("INSERT INTO chat (sender, message) VALUES (?,?)", ("AI", response_text))
                    conn.commit()
                except Exception as e:
                    st.error(f"Chat Error: {e}")
