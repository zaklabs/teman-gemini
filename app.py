# ============================================================================
# Nama Proyek  : Teman Gemini
# File         : app.py
# Deskripsi    : Aplikasi Streamlit utama untuk chatbot AI dengan fitur RAG
#                dokumen. Menyediakan interface chat interaktif dan analisis
#                dokumen PDF menggunakan Google Gemini.
# Pembuat      : Zaki Fuadi
# Versi        : v1.0
# Lisensi      : MIT
# ============================================================================
#
# Catatan:
# - Mendukung dua fitur utama: Chat AI dan Chat Dokumen (RAG)
# - Menggunakan model Google Gemini 2.0 Flash untuk percakapan
# - Mengimplementasikan persistensi riwayat chat menggunakan database SQLite
# - Menyediakan parameter AI yang dapat disesuaikan (temperature, top_p, top_k)
#
# ============================================================================

# Import library yang diperlukan
import streamlit as st  # Untuk membuat interface aplikasi web
from langchain_google_genai import ChatGoogleGenerativeAI  # Untuk berinteraksi dengan Google Gemini via LangChain
from langgraph.prebuilt import create_react_agent  # Untuk membuat ReAct agent
from langchain_core.messages import HumanMessage, AIMessage  # Untuk format pesan
import json
import os
import time
from database import ChatbotDatabase
from streamlit_lottie import st_lottie
import requests
from document_rag import DocumentRAG

# --- Custom CSS for Chat Layout ---
st.markdown("""
<style>
    /* Style for user messages (right-aligned) */
    .stChatMessage[data-testid="user-message"] {
        flex-direction: row-reverse;
        text-align: right;
    }
    
    .stChatMessage[data-testid="user-message"] .stMarkdown {
        background-color: #e3f2fd;
        border-radius: 15px;
        padding: 10px 15px;
        margin-left: auto;
    }
    
    /* Style for assistant messages (left-aligned) */
    .stChatMessage[data-testid="assistant-message"] {
        flex-direction: row;
        text-align: left;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stMarkdown {
        background-color: #f5f5f5;
        border-radius: 15px;
        padding: 10px 15px;
        margin-right: auto;
    }
    
    /* General chat styling */
    .stChatMessage {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Loading/Thinking animations
LOADING_ANIMATIONS = {
    "typing": "https://lottie.host/b0c3d6e6-d5a9-4b5e-9c3d-f3e8b5c9d8f1/typing.json",
    "dots": "https://assets5.lottiefiles.com/packages/lf20_a2chheio.json",
    "robot_thinking": "https://assets9.lottiefiles.com/packages/lf20_8nuwm3ed.json",
    "loading_bars": "https://assets5.lottiefiles.com/private_files/lf30_8npirptd.json",
    "ai_brain": "https://assets4.lottiefiles.com/packages/lf20_qjogjzyw.json",
    "chat_bubbles": "https://assets10.lottiefiles.com/packages/lf20_vd3zjrvg.json",
    "welcome": "https://lottie.host/6cc5c636-161e-4fe2-a29e-d0a010fb857d/oUxnN8jMLv.json",
    "google": "https://lottie.host/2966fd1b-0cf2-4c78-8fcc-004d350f3896/P4IUAgx8I3.lottie",
}

DEFAULT_ANIMATION = LOADING_ANIMATIONS["dots"]

# --- Fungsi Helper ---

def load_lottie_url(url: str):
    """Memuat animasi Lottie dari URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def simulate_typing(text: str, container):
    """Simulasi efek mengetik seperti ChatGPT :D"""
    full_response = ""
    message_placeholder = container.empty()
    
    # Pisahkan teks menjadi kata-kata untuk efek mengetik yang lebih halus
    words = text.split()
    
    for i, word in enumerate(words):
        full_response += word + " "
        # Tambahkan kursor mengetik
        message_placeholder.markdown(full_response + "▌")
        # Atur kecepatan: lebih cepat untuk kata pendek, lebih lambat untuk kata panjang
        time.sleep(0.05)
    
    # Tampilkan pesan akhir tanpa kursor
    message_placeholder.markdown(full_response)
    return full_response.strip()

# --- 1. Muat Konfigurasi ---

def load_config():
    """Memuat konfigurasi dari file config.json"""
    config_path = "config.json"
    
    if not os.path.exists(config_path):
        st.error("❌ Config file not found! Please create config.json with your Google API key.")
        st.stop()
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "google_api_key" not in config or config["google_api_key"] == "YOUR_GOOGLE_API_KEY_HERE":
            st.error("❌ Please set your Google API key in config.json")
            st.stop()
        
        return config
    except Exception as e:
        st.error(f"❌ Error loading config: {e}")
        st.stop()

# Muat konfigurasi
config = load_config()
google_api_key = config["google_api_key"]

# --- 2. Inisialisasi Database ---
@st.cache_resource
def get_database():
    """Inisialisasi dan kembalikan instance database"""
    return ChatbotDatabase()

db = get_database()

# --- 3. Konfigurasi Halaman dan Judul ---
col1, col2 = st.columns([1.5,8])
with col1:
    st_lottie(load_lottie_url(LOADING_ANIMATIONS["loading_bars"]), height=100, width=100, key="welcome")
with col2:
    st.title("Teman Gemini - AI Chatbot")
st.caption("Chat dengan asisten AI Cerdas menggunakan Google's Gemini model")

# --- 4. Autentikasi User (Input Nama) ---

# Cek apakah user sudah login
if "user_id" not in st.session_state or "username" not in st.session_state:
    st.subheader("🙋 Selamat Datang!")
    st.write("Silakan masukkan nama Anda untuk memulai.")
    
    # Buat form untuk input nama
    with st.form("user_login_form"):
        username = st.text_input("Nama Anda:", placeholder="Masukkan nama Anda di sini")
        submit_button = st.form_submit_button("Lanjutkan")
        
        if submit_button:
            if username.strip():
                # Buat atau ambil user
                user_id = db.create_user(username.strip())
                st.session_state.user_id = user_id
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("⚠️ Nama tidak boleh kosong!")
    
    st.stop()

# --- 5. Pemilihan Fitur (jika belum dipilih) ---

if "selected_feature" not in st.session_state:
    st.subheader(f"👋 Halo, {st.session_state.username}!")
    st.write("Pilih fitur yang ingin Anda gunakan:")
    
    # Buat dua kolom untuk tombol fitur
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 Chat AI")
        st.write("Berbincang dengan asisten AI cerdas")
        if st.button("🚀 Mulai Chat", key="btn_chat", use_container_width=True):
            st.session_state.selected_feature = "chat"
            st.rerun()
    
    with col2:
        st.markdown("### 📄 Chat dengan Dokumen")
        st.write("Upload PDF dan tanyakan apapun tentang isinya")
        if st.button("📚 Mulai Analisis", key="btn_document", use_container_width=True):
            st.session_state.selected_feature = "document"
            st.rerun()
            st.rerun()
    
    st.stop()

# --- 6. Sidebar untuk Info User dan Pengaturan ---

with st.sidebar:
    st.subheader(f"👤 {st.session_state.username}")
    st.write(f"User ID: {st.session_state.user_id}")
    
    st.divider()
    
    # Navigasi Fitur
    st.subheader("📍 Navigasi")
    current_feature = st.session_state.get("selected_feature", "chat")
    
    if st.button("💬 Chat AI", key="nav_chat", use_container_width=True, 
                 type="primary" if current_feature == "chat" else "secondary"):
        st.session_state.selected_feature = "chat"
        st.rerun()
    
    if st.button("📄 Chat Dokumen", key="nav_document", use_container_width=True,
                 type="primary" if current_feature == "document" else "secondary"):
        st.session_state.selected_feature = "document"
        st.rerun()
    
    st.divider()
    
    # Tombol kondisional berdasarkan fitur
    if current_feature == "chat":
        # Tombol reset percakapan (hanya untuk chat)
        if st.button("🔄 Reset Percakapan", help="Hapus semua pesan dan mulai dari awal"):
            db.clear_user_history(st.session_state.user_id)
            st.session_state.pop("messages", None)
            st.session_state.pop("agent", None)
            st.rerun()
    elif current_feature == "document":
        # Tombol hapus dokumen
        if st.button("🗑️ Hapus Dokumen", help="Hapus dokumen yang sudah diupload"):
            if "document_rag" in st.session_state:
                st.session_state.document_rag.cleanup()
            st.session_state.pop("document_rag", None)
            st.session_state.pop("document_qa_history", None)
            st.session_state.pop("uploaded_file_name", None)
            st.rerun()
    
    # Tombol logout
    if st.button("🚪 Logout", help="Keluar dan kembali ke halaman login"):
        # Bersihkan dokumen jika ada
        if "document_rag" in st.session_state:
            st.session_state.document_rag.cleanup()
        st.session_state.pop("user_id", None)
        st.session_state.pop("username", None)
        st.session_state.pop("messages", None)
        st.session_state.pop("agent", None)
        st.session_state.pop("selected_feature", None)
        st.session_state.pop("document_rag", None)
        st.session_state.pop("document_qa_history", None)
        st.rerun()
    
    st.divider()
    
    # Tampilkan statistik berdasarkan fitur
    if current_feature == "chat":
        st.subheader("📊 Statistik Chat")
        if "messages" in st.session_state:
            user_msgs = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
            assistant_msgs = sum(1 for msg in st.session_state.messages if msg["role"] == "assistant")
            st.metric("Pesan Anda", user_msgs)
            st.metric("Balasan AI", assistant_msgs)
        
        st.divider()
        
        # Pengaturan Parameter AI
        st.subheader("⚙️ Parameter AI")
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1,
                                help="Mengontrol kreativitas AI. Nilai lebih tinggi = lebih kreatif")
        top_p = st.slider("Top-p", min_value=0.0, max_value=1.0, value=0.95, step=0.05,
                          help="Nucleus sampling. Mengontrol keberagaman output")
        top_k = st.slider("Top-k", min_value=0, max_value=50, value=20, step=1,
                          help="Membatasi jumlah token yang dipertimbangkan")
        
        # Simpan di session state
        st.session_state.temperature = temperature
        st.session_state.top_p = top_p
        st.session_state.top_k = top_k
        
    elif current_feature == "document":
        st.subheader("📄 Info Dokumen")
        if "uploaded_file_name" in st.session_state:
            st.success(f"Dokumen: {st.session_state.uploaded_file_name}")
            if "document_qa_history" in st.session_state:
                st.metric("Pertanyaan", len(st.session_state.document_qa_history))
        else:
            st.info("Belum ada dokumen yang diupload")

# --- 7. Tampilkan Konten Berdasarkan Fitur yang Dipilih ---

if st.session_state.get("selected_feature") == "document":
    # ========== FITUR DOCUMENT RAG ==========
    st.header("📄 Chat dengan Dokumen")
    st.write("Upload dokumen PDF dan tanyakan apapun tentang isinya menggunakan AI")
    
    # Inisialisasi RAG jika belum ada
    if "document_rag" not in st.session_state:
        st.session_state.document_rag = DocumentRAG(google_api_key)
    
    # Inisialisasi riwayat QA jika belum ada
    if "document_qa_history" not in st.session_state:
        st.session_state.document_qa_history = []
    
    # File uploader
    st.subheader("1️⃣ Upload Dokumen PDF")
    uploaded_file = st.file_uploader(
        "Pilih file PDF",
        type=["pdf"],
        help="Upload file PDF yang ingin Anda analisis",
        key="pdf_uploader"
    )
    
    if uploaded_file is not None:
        # Cek apakah ini file baru
        if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            
            with st.spinner("Memproses dokumen..."):
                # Tampilkan animasi loading
                col_load1, col_load2 = st.columns([1, 3])
                with col_load1:
                    lottie_json = load_lottie_url(DEFAULT_ANIMATION)
                    if lottie_json:
                        st_lottie(lottie_json, height=80, key="doc_loading")
                with col_load2:
                    st.write("_Membaca dan menganalisis PDF..._")
                
                # Muat PDF
                success, message, num_pages = st.session_state.document_rag.load_pdf(uploaded_file)
                
                if success:
                    st.success(f"✅ {message}")
                    
                    # Dapatkan ringkasan dokumen
                    with st.spinner("Membuat ringkasan dokumen..."):
                        summary = st.session_state.document_rag.get_document_summary()
                        st.session_state.document_summary = summary
                    
                    # Reset riwayat QA untuk dokumen baru
                    st.session_state.document_qa_history = []
                else:
                    st.error(f"❌ {message}")
                    st.session_state.pop("uploaded_file_name", None)
        
        # Tampilkan info dokumen jika sudah dimuat
        if "uploaded_file_name" in st.session_state:
            st.markdown("---")
            st.subheader("📋 Informasi Dokumen")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Nama File:** {st.session_state.uploaded_file_name}")
            with col2:
                if "document_summary" in st.session_state:
                    with st.expander("📝 Ringkasan Dokumen"):
                        st.write(st.session_state.document_summary)
            
            # Bagian Q&A
            st.markdown("---")
            st.subheader("2️⃣ Tanyakan tentang Dokumen")
            
            # Tampilkan riwayat QA
            if st.session_state.document_qa_history:
                st.markdown("### 💬 Riwayat Percakapan")
                for i, qa in enumerate(st.session_state.document_qa_history):
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(qa["question"])
                    
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(qa["answer"])
                        
                        # Tampilkan sumber
                        if qa.get("sources"):
                            with st.expander(f"📚 Sumber (dari {len(qa['sources'])} bagian dokumen)"):
                                for j, source in enumerate(qa["sources"], 1):
                                    st.markdown(f"**Halaman {source['page'] + 1}:**")
                                    st.caption(source["content"])
                                    if j < len(qa["sources"]):
                                        st.markdown("---")
            
            # Input pertanyaan
            question = st.chat_input("Tanyakan sesuatu tentang dokumen ini...")
            
            if question:
                # Tambahkan pertanyaan ke tampilan riwayat
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(question)
                
                # Dapatkan jawaban dengan loading
                with st.chat_message("assistant", avatar="🤖"):
                    # Tampilkan loading
                    col_think1, col_think2 = st.columns([1, 4])
                    with col_think1:
                        lottie_json = load_lottie_url(DEFAULT_ANIMATION)
                        if lottie_json:
                            lottie_placeholder = st.empty()
                            with lottie_placeholder:
                                st_lottie(lottie_json, height=50, key=f"thinking_{len(st.session_state.document_qa_history)}")
                    
                    with col_think2:
                        status_placeholder = st.empty()
                        status_placeholder.markdown("_Mencari jawaban dalam dokumen..._")
                    
                    # Query dokumen
                    answer, sources = st.session_state.document_rag.query(question)
                    
                    # Hapus loading
                    if lottie_json:
                        lottie_placeholder.empty()
                    status_placeholder.empty()
                    
                    # Tampilkan jawaban dengan efek mengetik
                    answer_placeholder = st.empty()
                    simulate_typing(answer, answer_placeholder)
                    
                    # Tampilkan sumber
                    if sources:
                        with st.expander(f"📚 Sumber (dari {len(sources)} bagian dokumen)"):
                            for j, source in enumerate(sources, 1):
                                st.markdown(f"**Halaman {source['page'] + 1}:**")
                                st.caption(source["content"])
                                if j < len(sources):
                                    st.markdown("---")
                
                # Simpan ke riwayat
                st.session_state.document_qa_history.append({
                    "question": question,
                    "answer": answer,
                    "sources": sources
                })
                
                # Rerun untuk update tampilan
                st.rerun()
    
    else:
        # Tidak ada file yang diupload
        st.info("👆 Silakan upload file PDF untuk memulai")
        
        # Tampilkan contoh pertanyaan
        st.markdown("---")
        st.markdown("### 💡 Contoh Pertanyaan yang Bisa Anda Ajukan:")
        st.markdown("""
        - Apa topik utama yang dibahas dalam dokumen ini?
        - Ringkas dokumen ini dalam 3-5 poin
        - Apa kesimpulan dari dokumen ini?
        - Jelaskan tentang [topik spesifik] dalam dokumen
        - Apa saja data atau angka penting yang disebutkan?
        - Siapa saja yang disebutkan dalam dokumen?
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ Cara Penggunaan:")
        st.info("""
        1. **Upload PDF** - Pilih file PDF yang ingin Anda analisis
        2. **Tunggu Proses** - AI akan membaca dan memproses dokumen
        3. **Lihat Ringkasan** - Baca ringkasan otomatis dokumen
        4. **Tanyakan Apapun** - Ketik pertanyaan Anda di chat box
        5. **Dapatkan Jawaban** - AI akan menjawab berdasarkan isi dokumen
        6. **Cek Sumber** - Lihat dari halaman mana jawaban diambil
        """)

else:
    # ========== FITUR CHAT (Default) ==========
    st.header("💬 Chat dengan AI")
    
    # Dapatkan parameter dari session state (dari slider sidebar)
    temperature = st.session_state.get("temperature", 0.7)
    top_p = st.session_state.get("top_p", 0.95)
    top_k = st.session_state.get("top_k", 20)
    
    # --- Inisialisasi Agent untuk Chat ---
    # Reinisialisasi agent jika parameter berubah atau agent belum ada
    current_params = (temperature, top_p, top_k)
    stored_params = st.session_state.get("last_params", None)
    
    if "agent" not in st.session_state or current_params != stored_params:
        try:
            # Inisialisasi LLM dengan API key dan parameter dari slider
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=google_api_key,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            
            # Buat ReAct agent sederhana dengan LLM
            st.session_state.agent = create_react_agent(
                model=llm,
                tools=[],  # Tidak ada tools untuk contoh sederhana ini
                prompt=f"You are a helpful, friendly assistant chatting with {st.session_state.username}. Respond concisely and clearly in Indonesian when appropriate."
            )
            
            # Simpan parameter saat ini
            st.session_state.last_params = current_params
            
        except Exception as e:
            st.error(f"❌ Error initializing agent: {e}")
            st.stop()

    # --- Muat Riwayat Chat dari Database ---
    if "messages" not in st.session_state:
        # Muat riwayat chat dari database
        history = db.get_chat_history(st.session_state.user_id)
        st.session_state.messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in history
        ]

    # --- Tampilkan Pesan Sebelumnya ---
    for msg in st.session_state.messages:
        # Tentukan avatar berdasarkan role
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        
        # Tampilkan pesan dengan styling yang sesuai
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # --- Tangani Input User dan Komunikasi Agent ---
    
    # Buat chat input box
    prompt = st.chat_input("Ketik pesan Anda di sini...")

    if prompt:
        # 1. Tambahkan pesan user ke riwayat pesan
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Simpan pesan user ke database
        db.save_message(st.session_state.user_id, "user", prompt)
        
        # 3. Tampilkan pesan user
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # 4. Tampilkan animasi loading saat memproses
        with st.chat_message("assistant", avatar="🤖"):
            # Buat kolom untuk animasi loading
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Muat dan tampilkan animasi Lottie
                lottie_json = load_lottie_url(DEFAULT_ANIMATION)
                
                if lottie_json:
                    lottie_placeholder = st.empty()
                    with lottie_placeholder:
                        st_lottie(lottie_json, height=60, key="loading")
            
            with col2:
                status_placeholder = st.empty()
                status_placeholder.markdown("_Sedang berpikir..._")
            
            # 5. Dapatkan respon dari assistant
            try:
                # Konversi riwayat pesan ke format yang diharapkan agent
                messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
                
                # Kirim prompt user ke agent
                response = st.session_state.agent.invoke({"messages": messages})
                
                # Ekstrak jawaban dari respon
                if "messages" in response and len(response["messages"]) > 0:
                    answer = response["messages"][-1].content
                else:
                    answer = "Maaf, saya tidak bisa menghasilkan respons."

            except Exception as e:
                answer = f"Terjadi kesalahan: {e}"
            
            # Hapus animasi loading
            if lottie_json:
                lottie_placeholder.empty()
            status_placeholder.empty()
            
            # 6. Tampilkan respon assistant dengan efek mengetik
            response_container = st.empty()
            final_answer = simulate_typing(answer, response_container)
        
        # 7. Tambahkan respon assistant ke riwayat pesan
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # 8. Simpan pesan assistant ke database
        db.save_message(st.session_state.user_id, "assistant", answer)
        
        # 9. Rerun untuk menampilkan pesan dengan format yang tepat
        st.rerun()
