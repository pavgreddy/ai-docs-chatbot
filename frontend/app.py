import streamlit as st
import requests

st.set_page_config(
    page_title="AI Docs Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    .chat-message-user {
        background: #0066ff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
    }
    .chat-message-bot {
        background: white;
        color: #1a1a1a;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 70%;
        border: 1px solid #e0e0e0;
    }
    .source-box {
        background: #f0f4ff;
        border-left: 3px solid #0066ff;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        color: #555;
        margin-top: 4px;
    }
    .upload-section {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }
    .header-title {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a1a;
    }
    .header-sub {
        color: #666;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "http://127.0.0.1:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📄 Document")
    st.markdown('<p class="header-sub">Upload a PDF to get started</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        if st.session_state.uploaded_filename != uploaded_file.name:
            with st.spinner("Indexing your document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/upload-pdf", files=files)
                if response.status_code == 200:
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.session_state.messages = []
                    st.success(f"✅ {uploaded_file.name} indexed!")
                else:
                    st.error("Upload failed. Make sure the backend is running.")

    if st.session_state.uploaded_filename:
        st.info(f"📎 **{st.session_state.uploaded_filename}**")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 💬 Chat")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-bot">{msg["content"]}</div>', unsafe_allow_html=True)
                if msg.get("sources"):
                    with st.expander("📚 View sources"):
                        for source in msg["sources"]:
                            st.markdown(f'<div class="source-box">{source}...</div>', unsafe_allow_html=True)

    if st.session_state.uploaded_filename:
        question = st.chat_input("Ask a question about your document...")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                response = requests.post(f"{BACKEND_URL}/chat", json={
                    "question": question,
                    "filename": st.session_state.uploaded_filename
                })
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data.get("sources", [])
                    })
            st.rerun()
    else:
        st.info("👈 Upload a PDF first to start chatting!")