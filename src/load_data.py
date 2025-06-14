import mysql.connector as sql
import fitz
import os
import random
from getpass import getpass
from faker import Faker
from core.encryption_handler import encrypt
from core.config_manager import get_db_config, save_db_config

# --- Konfigurasi ---
SEED = 42

def get_credentials():
    """Membaca konfigurasi DB atau memintanya dari pengguna jika tidak ada."""
    config = get_db_config()
    if config and config.get('password') is not None:
        print("Konfigurasi database dimuat dari config.ini.")
        return config['user'], config['password'], config['database']
    else:
        print("Konfigurasi database tidak ditemukan atau tidak lengkap.")
        user = input("Masukkan username MySQL Anda (default: root): ") or "root"
        password = getpass("Masukkan password MySQL Anda (tekan Enter jika tidak ada): ")
        db_name = "cv_application"
        # Simpan konfigurasi untuk penggunaan selanjutnya
        save_db_config(user, password, db_name)
        return user, password, db_name

def generate_fake_data(length):
    faker = Faker()
    primer_key = {}
    for i in range(length):
        primer_key[i] = {
            "first_name": faker.first_name(), "last_name": faker.last_name(),
            "date_of_birth": faker.date_of_birth(), "address": faker.address().replace('\n', ', '),
            "phone_number": faker.phone_number()
        }
    return primer_key

def extract_pdf_role(path):
    try:
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc: return doc[0].get_text().strip().split('\n')[0]
    except Exception: pass
    return "Unknown Role"

def main():
    """Fungsi utama untuk membersihkan dan mengisi ulang database."""
    Faker.seed(SEED)
    random.seed(SEED)
    
    DB_USER, DB_PASS, DB_NAME = get_credentials()

    try:
        # Koneksi tanpa memilih database untuk bisa melakukan DROP
        connect = sql.connect(host="localhost", user=DB_USER, password=DB_PASS)
        cursor = connect.cursor()
        print(f"Membersihkan database lama '{DB_NAME}' (jika ada)...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print("Membuat database baru...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        # Membuat tabel setelah database bersih
        cursor.execute("""
            CREATE TABLE ApplicantProfile (
                applicant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                first_name BLOB, last_name BLOB, date_of_birth BLOB,
                address BLOB, phone_number BLOB
            )""")
        cursor.execute("""
            CREATE TABLE ApplicationDetail (
                detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                application_role VARCHAR(200) DEFAULT NULL,
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
            )""")

        # Persiapan data
        data_dir = "data"
        if not os.path.isdir(data_dir):
            print(f"Error: Folder '{data_dir}' tidak ditemukan. Pastikan skrip dijalankan dari root direktori proyek.")
            return

        id_len, primer_key = 400, generate_fake_data(400)
        fields = os.listdir(data_dir)

        print("Memulai proses memuat data baru ke MySQL...")
        for field in fields:
            field_path = os.path.join(data_dir, field)
            if not os.path.isdir(field_path): continue

            fnames = sorted(os.listdir(field_path))
            print(f"  Memproses kategori: {field}...")
            for j in range(min(20, len(fnames))):
                applicant_data = primer_key[random.randint(0, id_len - 1)]
                full_cv_path = os.path.join(field_path, fnames[j])
                
                encrypted_data = (
                    encrypt(applicant_data['first_name']), encrypt(applicant_data['last_name']),
                    encrypt(applicant_data['date_of_birth']), encrypt(applicant_data['address']),
                    encrypt(applicant_data['phone_number'])
                )
                
                insert_applicant = "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_applicant, encrypted_data)
                applicant_id = cursor.lastrowid

                role = extract_pdf_role(full_cv_path)
                absolute_path = os.path.abspath(full_cv_path)
                application_data = (applicant_id, f"{role}, {field}", absolute_path)
                insert_role = "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)"
                cursor.execute(insert_role, application_data)

        connect.commit()
        print("\nProses memuat data selesai dengan sukses.")

    except sql.Error as err:
        print(f"Database Error: {err}")
        if 'connect' in locals() and connect.is_connected(): connect.rollback()
    finally:
        if 'connect' in locals() and connect.is_connected():
            cursor.close()
            connect.close()


if __name__ == "__main__":
    main()

