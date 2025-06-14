from faker import Faker
import mysql.connector as sql
import fitz
import os
import random
from core.encryption_handler import encrypt

# --- Konfigurasi ---
SEED = 42
DB_NAME = "cv_application"
DB_USER = "root"
DB_PASS = input("Masukkan password MySQL Anda: ") or "sqlmantap"  # Ganti dengan password MySQL Anda

def generate_fake_data(length):
    faker = Faker()
    primer_key = {}
    for i in range(length):
        primer_key[i] = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "date_of_birth": faker.date_of_birth(),
            "address": faker.address().replace('\n', ', '),
            "phone_number": faker.phone_number()
        }
    return primer_key

def extract_pdf_role(path):
    try:
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(document) > 0:
            return document[0].get_text().strip().split('\n')[0]
    except Exception: return "Unknown Role"
    return "Unknown Role"

def setup_database_and_load(db_name, user, password, applicant_data, application_data):
    try:
        connect = sql.connect(host="localhost", user=user, password=password)
        cursor = connect.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                first_name BLOB, last_name BLOB, date_of_birth BLOB,
                address BLOB, phone_number BLOB
            )""")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                application_role VARCHAR(200) DEFAULT NULL,
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
            )""")

        encrypted_fname = encrypt(applicant_data['first_name'])
        encrypted_lname = encrypt(applicant_data['last_name'])
        encrypted_phone = encrypt(applicant_data['phone_number'])
        encrypted_birth = encrypt(applicant_data['date_of_birth'])
        encrypted_address = encrypt(applicant_data['address'])
        
        insert_applicant = "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_applicant, (encrypted_fname, encrypted_lname, encrypted_birth, encrypted_address, encrypted_phone))
        applicant_id = cursor.lastrowid

        insert_role = "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)"
        cursor.execute(insert_role, (applicant_id, application_data[0], application_data[1]))
        connect.commit()

    except sql.Error as err:
        print(f"Database Error: {err}")
        if 'connect' in locals() and connect.is_connected(): connect.rollback()
    finally:
        if 'connect' in locals() and connect.is_connected(): cursor.close(); connect.close()

def main():
    """Fungsi utama untuk menjalankan proses seeding data."""
    # Karena skrip dijalankan dari root, path ke data adalah 'data/'
    data_dir = "data"
    
    if not os.path.isdir(data_dir):
        print(f"Error: Folder '{data_dir}' tidak ditemukan. Pastikan skrip dijalankan dari root direktori proyek.")
        return

    fields = os.listdir(data_dir)
    id_len, primer_key = 400, generate_fake_data(400)

    print("Memulai proses memuat data ke MySQL...")
    for field in fields:
        field_path = os.path.join(data_dir, field)
        if not os.path.isdir(field_path): continue

        fnames = sorted(os.listdir(field_path))
        print(f"  Memproses kategori: {field}...")
        for j in range(min(20, len(fnames))):
            random_applicant_id = random.randint(0, id_len - 1)
            fname = fnames[j]

            full_cv_path = os.path.join(field_path, fname)
            role = extract_pdf_role(full_cv_path)
            
            # --- PERBAIKAN DI SINI ---
            # Mengubah path relatif menjadi path absolut untuk disimpan di database
            absolute_path_for_db = os.path.abspath(full_cv_path)
            
            application_data = (f"{role}, {field}", absolute_path_for_db)
            setup_database_and_load(DB_NAME, DB_USER, DB_PASS, primer_key[random_applicant_id], application_data)

    print("\nProses memuat data selesai.")

if __name__ == "__main__":
    main()
