# 🤖 Teman Gemini - AI Chatbot
![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Hacktive8](https://academic.hacktiv8.com/static/media/hacktiv-navbar.35edca5f.png)

![image](assets/flyer1.jpg)

Streamlit Cloud [Teman Gemini](https://teman-gemini.streamlit.app)

Aplikasi ini merupakan final project dari pelatihan "LLM-Based Tools and Gemini API Integration for Data Scientists" yang diselenggarakan oleh Hacktive8. Program ini merupakan bagian dari AI Opportunity Fund: Asia Pacific, yang bekerja sama dengan AVPN serta didukung oleh Google.org dan Asian Development Bank (ADB).


## ✨ Fitur

### 💬 Chat AI
- Percakapan interaktif dengan Google Gemini 2.0 Flash
- Riwayat chat tersimpan otomatis di database SQLite
- Parameter AI yang dapat disesuaikan (Temperature, Top-p, Top-k)
- Efek typing animasi seperti ChatGPT (non-stream)
- Multi-user support dengan autentikasi nama
- Statistik percakapan real-time

### 📄 Chat dengan Dokumen (RAG)
- Upload dan analisis dokumen PDF
- Pertanyaan & jawaban berbasis konten dokumen
- Semantic search menggunakan vector embeddings
- Ringkasan dokumen otomatis
- Sumber referensi untuk setiap jawaban (dengan nomor halaman)
- Riwayat pertanyaan & jawaban

### 🎨 User Interface
- Interface yang bersih dan modern
- Animasi Lottie untuk loading states
- Sidebar navigasi yang intuitif
- Responsive design
- Custom CSS untuk styling pesan chat

## 📋 Persyaratan

### Sistem
- Python 3.13 atau lebih tinggi (disrankan gunakan miniconda)
- pip (Python package manager)
- Google API Key untuk Gemini

### Dependencies
Semua dependencies tercantum dalam file `requirements.txt`

## 🚀 Cara Install dan Setup

### 1. Clone atau Download Repository
```bash
git clone <repository-url>
cd temangemini
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Konfigurasi

Buat file `config.json` di root directory dengan format berikut:

```json
{
    "google_api_key": "YOUR_GOOGLE_API_KEY_HERE"
}
```

**Cara mendapatkan Google API Key:**
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan akun Google
3. Klik "Create API Key"
4. Copy API key dan paste ke `config.json`

> **Catatan:** File `config.example.json` disediakan sebagai template.

### 5. Jalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`

## 🛠️ Teknologi yang Digunakan

### Framework & Library Utama
- **[Streamlit](https://streamlit.io/)** - Framework web app untuk Python
- **[LangChain](https://www.langchain.com/)** - Framework untuk aplikasi LLM
- **[Google Gemini](https://ai.google.dev/)** - Large Language Model dari Google

### AI & Machine Learning
- **Google Generative AI** - Chat completion dan embeddings
- **LangGraph** - Untuk membuat ReAct agents
- **ChromaDB** - Vector database untuk semantic search

### Document Processing
- **PyPDF** - PDF loader untuk membaca dokumen
- **RecursiveCharacterTextSplitter** - Text chunking untuk RAG

### Database & Storage
- **SQLite** - Database lokal untuk menyimpan user dan chat history

### UI/UX
- **Streamlit-Lottie** - Animasi loading interaktif
- **Custom CSS** - Styling untuk interface chat

## 📁 Struktur Proyek

```
temangemini/
│
├── app.py                  # Aplikasi utama Streamlit
├── database.py             # Modul manajemen database
├── document_rag.py         # Modul RAG untuk dokumen PDF
├── requirements.txt        # Python dependencies
├── config.json            # Konfigurasi API key (buat manual)
├── config.example.json    # Template konfigurasi
├── chatbot.db            # Database SQLite (dibuat otomatis)
└── README.md             # Dokumentasi proyek
```

## 💡 Cara Penggunaan

### Chat AI
1. Masukkan nama Anda saat login
2. Pilih fitur "Chat AI"
3. Mulai berbincang dengan asisten AI
4. Sesuaikan parameter AI di sidebar (opsional)
5. Gunakan "Reset Percakapan" untuk memulai chat baru

### Chat Dokumen
1. Pilih fitur "Chat dengan Dokumen"
2. Upload file PDF Anda
3. Tunggu proses analisis selesai
4. Baca ringkasan dokumen
5. Tanyakan apapun tentang isi dokumen
6. Lihat sumber referensi dari jawaban AI

## 🔧 Konfigurasi Parameter AI

Parameter AI dapat disesuaikan di sidebar (fitur Chat AI):

- **Temperature (0.0 - 2.0)**: Mengontrol kreativitas AI
  - Nilai rendah = lebih konsisten dan faktual
  - Nilai tinggi = lebih kreatif dan variatif

- **Top-p (0.0 - 1.0)**: Nucleus sampling
  - Mengontrol keberagaman output

- **Top-k (0 - 50)**: Membatasi token yang dipertimbangkan
  - Nilai rendah = lebih fokus
  - Nilai tinggi = lebih beragam

## ⚠️ Troubleshooting

### Error: "Config file not found"
- Pastikan file `config.json` ada di root directory
- Copy dari `config.example.json` dan isi dengan API key Anda

### Error: "Please set your Google API key"
- Periksa format `config.json`
- Pastikan API key sudah diisi dengan benar
- Verifikasi API key di Google AI Studio

### PDF tidak terbaca
- Pastikan file PDF tidak terenkripsi/password protected
- Coba PDF lain untuk memastikan masalahnya bukan di file

### Animasi tidak muncul
- Periksa koneksi internet (animasi Lottie dimuat dari URL)
- Browser mungkin memblokir konten eksternal

## 📝 License

MIT License


## 👤 Author

**Zaki Fuadi**

- GitHub: [@zaklabs](https://github.com/zaklabs)
- Email: support@zaklabs.my.id

---

⭐ **Jika project ini membantu Anda, berikan star di GitHub!**

📫 **Pertanyaan atau saran? Buka issue di GitHub repository.**
