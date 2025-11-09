# ============================================================================
# Nama Proyek  : Teman Gemini
# File         : database.py
# Deskripsi    : Modul database untuk chatbot. Menangani semua operasi database
#                termasuk manajemen user dan persistensi riwayat chat menggunakan
#                SQLite.
# Pembuat      : Zaki Fuadi
# Versi        : v1.0
# Lisensi      : MIT
# ============================================================================
#
# Catatan:
# - Menggunakan SQLite untuk penyimpanan database lokal
# - Mengelola dua tabel utama: users dan chat_history
# - Mendukung operasi CRUD untuk users dan pesan chat
#
# ============================================================================

"""
Modul database untuk chatbot
Menangani semua operasi database termasuk manajemen user dan riwayat chat
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class ChatbotDatabase:
    """Pengelola database untuk aplikasi chatbot"""
    
    def __init__(self, db_path: str = "chatbot.db"):
        """Inisialisasi koneksi database dan buat tabel jika belum ada"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Buat dan kembalikan koneksi database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Ini mengaktifkan akses kolom berdasarkan nama
        return conn
    
    def init_database(self):
        """Buat tabel database jika belum ada"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Buat tabel users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Buat tabel chat_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, name: str) -> int:
        """
        Buat user baru atau dapatkan ID user yang sudah ada
        
        Args:
            name: Nama user
            
        Returns:
            ID User
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # User sudah ada, dapatkan ID mereka
            cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
            user_id = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_id(self, name: str) -> Optional[int]:
        """
        Dapatkan ID user berdasarkan nama
        
        Args:
            name: Nama user
            
        Returns:
            ID User atau None jika tidak ditemukan
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def save_message(self, user_id: int, role: str, content: str):
        """
        Simpan pesan chat ke database
        
        Args:
            user_id: ID User
            role: Role pesan ('user' atau 'assistant')
            content: Konten pesan
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """
        Dapatkan riwayat chat untuk user
        
        Args:
            user_id: ID User
            limit: Jumlah maksimum pesan yang diambil (None untuk semua)
            
        Returns:
            List pesan sebagai dictionary
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT role, content, timestamp 
            FROM chat_history 
            WHERE user_id = ? 
            ORDER BY timestamp ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        conn.close()
        
        # Konversi rows menjadi list dictionary
        messages = []
        for row in rows:
            messages.append({
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"]
            })
        
        return messages
    
    def clear_user_history(self, user_id: int):
        """
        Hapus semua riwayat chat untuk user
        
        Args:
            user_id: ID User
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """
        Dapatkan semua user dari database
        
        Returns:
            List user sebagai dictionary
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"]
            })
        
        return users
