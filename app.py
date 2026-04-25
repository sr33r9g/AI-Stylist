import streamlit as st
import socket
import pickle
import struct

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Stylist Pro", page_icon="✨", layout="wide")

# ---------------- SESSION STATE ----------------
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

if "uploaded_bytes" not in st.session_state:
    st.session_state.uploaded_bytes = None

if "occasion_text" not in st.session_state:
    st.session_state.occasion_text = ""

# ---------------- CSS (FINAL FIX) ----------------
st.markdown("""
<style>

/* Layout base */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1280px !important;
}

/* Column alignment */
[data-testid="stHorizontalBlock"] {
    align-items: flex-start;
    gap: 1.5rem;
}

/* ✅ LEFT PANEL SCROLL */
[data-testid="stHorizontalBlock"] > div:first-child {
    max-height: calc(100vh - 140px);
    overflow-y: auto;
    padding-right: 8px;
    scroll-behavior: smooth;
}

/* ✅ RIGHT PANEL STICKY */
[data-testid="stHorizontalBlock"] > div:last-child {
    position: sticky;
    top: 1rem;
    align-self: flex-start;
}

/* Upload box */
section[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.03);
    border: 1px dashed rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 0.8rem;
}

/* Image */
.stImage > img {
    width: 100% !important;
    max-width: 320px;
    max-height: 300px;
    object-fit: contain;
    border-radius: 14px;
    background: #111;
    margin: 10px 0;
}

/* Textarea */
textarea {
    border-radius: 12px !important;
}

/* Buttons */
.stButton > button {
    height: 3em;
    border-radius: 10px;
    font-weight: 600;
}

/* Output panel */
.output-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid #6C63FF;
    border-radius: 14px;
    padding: 18px;
    min-height: 65vh;
    max-height: 75vh;
    overflow-y: auto;
    line-height: 1.6;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SOCKET ----------------
def stream_advice(image_bytes, occasion_text, host='127.0.0.1', port=5000):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((host, port))

        payload = pickle.dumps({
            "occasion": occasion_text,
            "image_bytes": image_bytes
        })

        header = struct.pack("Q", len(payload))
        client_socket.sendall(header + payload)

        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            yield chunk.decode("utf-8", errors="ignore")

    except Exception as e:
        yield f"⚠️ Error: {e}"

    finally:
        client_socket.close()

# ---------------- HEADER ----------------
st.markdown("# ✨ AI Stylist Pro")
st.caption("AI-powered wardrobe intelligence")
st.divider()

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1, 1.4], gap="large")

# ---------------- LEFT PANEL ----------------
with col1:
    st.markdown("### 🛠 Configuration")

    uploaded_file = st.file_uploader(
        "Upload Outfit",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:
        st.image(uploaded_file)

    occasion = st.text_area(
        "Occasion Details",
        value=st.session_state.occasion_text,
        placeholder="e.g. Job interview, wedding...",
        height=100
    )

    btn1, btn2 = st.columns(2)

    with btn1:
        generate = st.button("Generate Advice", use_container_width=True)

    with btn2:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        st.session_state.run_analysis = False
        st.session_state.analysis_text = ""
        st.session_state.uploaded_bytes = None
        st.session_state.occasion_text = ""
        st.rerun()

    if generate:
        if not uploaded_file:
            st.warning("Upload image first")
        elif not occasion.strip():
            st.warning("Enter occasion")
        else:
            st.session_state.uploaded_bytes = uploaded_file.getvalue()
            st.session_state.occasion_text = occasion
            st.session_state.run_analysis = True
            st.session_state.analysis_text = ""

# ---------------- RIGHT PANEL ----------------
with col2:
    st.markdown("### 🧠 Style Analysis")

    output = st.empty()

    if st.session_state.run_analysis:
        full_text = ""

        with st.spinner("Analyzing..."):
            for chunk in stream_advice(
                st.session_state.uploaded_bytes,
                st.session_state.occasion_text
            ):
                full_text += chunk
                output.markdown(
                    f'<div class="output-box">{full_text}</div>',
                    unsafe_allow_html=True
                )

        st.session_state.analysis_text = full_text
        st.session_state.run_analysis = False

    elif st.session_state.analysis_text:
        output.markdown(
            f'<div class="output-box">{st.session_state.analysis_text}</div>',
            unsafe_allow_html=True
        )

    else:
        output.markdown(
            '<div class="output-box"><i>Upload image and generate advice</i></div>',
            unsafe_allow_html=True
        )