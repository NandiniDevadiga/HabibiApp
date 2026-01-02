import streamlit as st
import google.generativeai as genai
import sqlite3

# --- 1. SETUP ---
st.set_page_config(page_title="Habibi Dubai Guide", layout="wide")
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash') # Use stable name

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect("habibi.db")
    conn.execute("CREATE TABLE IF NOT EXISTS chat (sender TEXT, message TEXT)")
    conn.commit()
    return conn

conn = init_db()

# --- 3. UI TABS ---
st.title("Habibi Dubai Guide 🌴")
tab1, tab2, tab3 = st.tabs(["Translate", "Explore", "AI Chat"])

with tab1:
    st.header("Arabic Translator")
    text = st.text_input("Enter English word:")
    if st.button("Translate"):
        res = model.generate_content(f"Translate '{text}' to Arabic with pronunciation.")
        st.success(res.text)

with tab2:
    st.header("Explore Dubai")
    if st.button("Find Attractions"):
        res = model.generate_content("List 3 top attractions in Dubai with prices.")
        st.write(res.text)

with tab3:
    st.header("Chat with Habibi")
    user_msg = st.chat_input("Ask me anything about Dubai...")
    if user_msg:
        res = model.generate_content(user_msg)
        st.chat_message("user").write(user_msg)
        st.chat_message("assistant").write(res.text)
        # Save to DB
        conn.execute("INSERT INTO chat VALUES (?,?)", ("User", user_msg))
        conn.execute("INSERT INTO chat VALUES (?,?)", ("AI", res.text))
        conn.commit()
