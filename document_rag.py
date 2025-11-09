# ============================================================================
# Nama Proyek  : Teman Gemini
# File         : document_rag.py
# Deskripsi    : Modul RAG (Retrieval Augmented Generation) untuk memproses
#                dan melakukan query dokumen PDF menggunakan Google Gemini
#                embeddings dan pencarian vektor dengan ChromaDB.
# Pembuat      : Zaki Fuadi
# Versi        : v1.0
# Lisensi      : MIT
# ============================================================================
#
# Catatan:
# - Menggunakan LangChain untuk pemrosesan dan retrieval dokumen
# - Mengimplementasikan pencarian vektor menggunakan ChromaDB untuk semantic search
# - Mendukung loading dokumen PDF, chunking, dan Q&A
# - Menggunakan model embedding Google Gemini: gemini-embedding-exp-03-07
#
# ============================================================================

"""
Modul RAG (Retrieval Augmented Generation)
Untuk membaca dan memproses dokumen PDF menggunakan Google Gemini
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import tempfile
import os
import shutil


class DocumentRAG:
    """Class untuk menangani RAG dengan dokumen PDF"""
    
    def __init__(self, api_key: str):
        """
        Inisialisasi sistem RAG
        
        Args:
            api_key: Google API key
        """
        self.api_key = api_key
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-exp-03-07",
            google_api_key=api_key
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.3
        )
        self.vectorstore = None
        self.qa_chain = None
        self.documents = []
        self.temp_dir = None
        
    def load_pdf(self, uploaded_file):
        """
        Muat dan proses file PDF
        
        Args:
            uploaded_file: Objek file yang diupload dari Streamlit
            
        Returns:
            tuple: (success: bool, message: str, num_pages: int)
        """
        try:
            # Buat direktori sementara
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            
            self.temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(self.temp_dir, uploaded_file.name)
            
            # Simpan file yang diupload ke temp
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Muat PDF
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
            
            if not documents:
                return False, "Gagal membaca PDF. File mungkin kosong atau rusak.", 0
            
            # Pisahkan dokumen menjadi chunk
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            self.documents = text_splitter.split_documents(documents)
            
            # Buat vector store
            self.vectorstore = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                persist_directory=os.path.join(self.temp_dir, "chroma_db")
            )
            
            # Buat QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
            
            num_pages = len(documents)
            num_chunks = len(self.documents)
            
            return True, f"Berhasil memproses {num_pages} halaman menjadi {num_chunks} bagian.", num_pages
            
        except Exception as e:
            return False, f"Error saat memproses PDF: {str(e)}", 0
    
    def query(self, question: str):
        """
        Query dokumen
        
        Args:
            question: Pertanyaan user
            
        Returns:
            tuple: (answer: str, sources: list)
        """
        if not self.qa_chain:
            return "Silakan upload dokumen terlebih dahulu.", []
        
        try:
            result = self.qa_chain({"query": question})
            answer = result["result"]
            
            # Dapatkan dokumen sumber
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    page_num = doc.metadata.get("page", "Unknown")
                    sources.append({
                        "page": page_num,
                        "content": doc.page_content[:200] + "..."
                    })
            
            return answer, sources
            
        except Exception as e:
            return f"Error saat memproses pertanyaan: {str(e)}", []
    
    def get_document_summary(self):
        """
        Dapatkan ringkasan dokumen yang dimuat
        
        Returns:
            str: Ringkasan dokumen
        """
        if not self.documents:
            return "Belum ada dokumen yang dimuat."
        
        try:
            # Ambil beberapa chunk pertama untuk konteks
            context = "\n\n".join([doc.page_content for doc in self.documents[:3]])
            
            prompt = f"""
            Berdasarkan teks berikut, buatlah ringkasan singkat tentang isi dokumen:
            
            {context}
            
            Ringkasan (maksimal 3-4 kalimat):
            """
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"Error membuat ringkasan: {str(e)}"
    
    def cleanup(self):
        """Bersihkan file sementara"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
    
    def __del__(self):
        """Destructor untuk cleanup"""
        self.cleanup()
