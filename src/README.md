src/
├── assets/
│   └── JacquesFrancois-Regular.ttf
├── config.py             # Menyimpan konstanta seperti palet warna & font
├── ui/
│   ├── __init__.py
│   ├── main_window.py    # Kelas utama aplikasi (App)
│   ├── summary_window.py # Kelas untuk jendela detail CV
│   └── widgets.py        # Kelas untuk komponen UI kustom (WarningPopup, CVCard)
├── core/
│   ├── __init__.py
│   └── data_manager.py   # Mengelola pengambilan data (saat ini dummy)
|   └── algorithms.py     # implementasi algoritma disini
|   └── db_connector.py    # mendapatkan data dari database
|   └── search_handler.py
└── main.py               # Titik masuk utama untuk menjalankan aplikasi
└── load_data.py          # jalankan ini untuk inisiasi database

Cara inisiasi database:
1. install mysql
2. buka terminal, jalankan "mysql -u root -p"
3. pada load_data.py line 11, ganti dengan paosswordmu
4. jalanin file load_data.py dari root 
"➜  -Tubes3_ParaPencariKerja git:(main) ✗ python3 src/load_data.py"git 