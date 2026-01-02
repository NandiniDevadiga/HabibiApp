import streamlit as st
import google.generativeai as genai
import sqlite3

# 1. SETUP
st.set_page_config(page_title="Habibi Dubai Guide", layout="wide", page_icon="🌴")

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("Missing API Key!")
    st.stop()

# USE THE 2026 DEFAULT MODEL
model = genai.GenerativeModel('gemini-3-flash')

# 2. DATABASE
def init_db():
    conn = sqlite3.connect("habibi.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS chat (sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn

conn = init_db()

# 3. UI
st.title("Habibi Dubai Guide 🌴")
tab1, tab2, tab3 = st.tabs(["🈯 Translator", "📍 Explore Dubai", "💬 Chat with Habibi"])

with tab1:
    st.header("English to Arabic")
    text_to_translate = st.text_input("Enter text:", key="trans_input")
    if st.button("Translate Now"):
        if text_to_translate:
            try:
                res = model.generate_content(f"Translate '{text_to_translate}' to Arabic.")
                st.success(res.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

with tab2:
    st.header("Recommendations")
    cat = st.selectbox("Category:", ["Top Attractions", "Luxury Hotels", "Budget Eats"])
    if st.button("Get Tips"):
        try:
            res = model.generate_content(f"List 3 {cat} in Dubai.")
            st.info(res.text)
        except Exception as e:
            st.error(f"AI Error: {e}")

with tab3:
    st.header("Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if p := st.chat_input("Ask Habibi..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.chat_message("assistant"):
            try:
                r = model.generate_content(p).text
                st.markdown(r)
                st.session_state.messages.append({"role": "assistant", "content": r})
            except Exception as e:
                st.error(f"Chat Error: {e}")
