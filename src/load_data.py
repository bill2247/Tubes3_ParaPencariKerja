from faker import Faker
import mysql.connector as sql
import fitz # PyMuPDF
import os
import random

# --- Konfigurasi ---
SEED = 42
DB_NAME = "cv_application"
DB_USER = "root"
DB_PASS = "sqlmantap" # Ganti dengan password MySQL Anda

# --- Inisialisasi ---
random.seed(SEED)
Faker.seed(SEED)

def generate_fake_data(length):
    """Membuat data profil pelamar palsu."""
    faker = Faker()
    primer_key = {}
    for i in range(length):
        primer_key[i] = (
            faker.first_name(),
            faker.last_name(),
            faker.date_of_birth(),
            faker.address().replace('\n', ', '),
            faker.phone_number()
        )
    return primer_key

def extract_pdf_role(path):
    """Mengekstrak hanya role dari halaman pertama PDF untuk efisiensi."""
    try:
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        if len(document) > 0:
            return document[0].get_text().strip().split('\n')[0]
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return "Unknown Role"
    return "Unknown Role"

def setup_database_and_load(db_name, user, password, applicant_data, application_data):
    """Menghubungkan ke DB, membuat tabel, dan memuat satu baris data."""
    try:
        connect = sql.connect(host="localhost", user=user, password=password)
        cursor = connect.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) DEFAULT NULL,
                last_name VARCHAR(50) DEFAULT NULL,
                date_of_birth DATE DEFAULT NULL,
                address VARCHAR(255) DEFAULT NULL,
                phone_number VARCHAR(30) DEFAULT NULL
            )""")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                application_role VARCHAR(200) DEFAULT NULL,
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
            )""")

        check_query = "SELECT applicant_id FROM ApplicantProfile WHERE first_name = %s AND last_name = %s AND phone_number = %s"
        cursor.execute(check_query, (applicant_data[0], applicant_data[1], applicant_data[4]))
        is_available = cursor.fetchone()

        if is_available:
            applicant_id = is_available[0]
        else:
            insert_applicant = "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_applicant, applicant_data)
            applicant_id = cursor.lastrowid

        insert_role = "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)"
        cursor.execute(insert_role, (applicant_id, application_data[0], application_data[1]))
        connect.commit()

    except sql.Error as err:
        print(f"Database Error: {err}")
        if 'connect' in locals() and connect.is_connected():
            connect.rollback()
    finally:
        if 'connect' in locals() and connect.is_connected():
            cursor.close()
            connect.close()

def main():
    """Fungsi utama untuk menjalankan proses seeding data."""
    # Menentukan path secara dinamis berdasarkan lokasi file skrip ini
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    data_dir = os.path.join(project_root, "data")
    
    if not os.path.isdir(data_dir):
        print(f"Error: Folder data tidak ditemukan di '{data_dir}'.")
        return

    fields = os.listdir(data_dir)
    
    id_len = 400
    primer_key = generate_fake_data(id_len)

    print("Memulai proses memuat data ke MySQL...")
    for field in fields:
        field_path = os.path.join(data_dir, field)
        if not os.path.isdir(field_path):
            continue

        fnames = os.listdir(field_path)
        fnames.sort()

        print(f"  Memproses kategori: {field}...")
        for j in range(min(20, len(fnames))):
            random_applicant_id = random.randint(0, id_len - 1)
            fname = fnames[j]

            full_cv_path = os.path.join(field_path, fname)
            role = extract_pdf_role(full_cv_path)
            
            db_cv_path = f"{field}/{fname}"
            application_role = f"{role}, {field}"
            application_data = (application_role, db_cv_path)

            setup_database_and_load(DB_NAME, DB_USER, DB_PASS, primer_key[random_applicant_id], application_data)

    print("\nProses memuat data selesai.")


if __name__ == "__main__":
    main()
