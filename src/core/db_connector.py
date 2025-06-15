import mysql.connector as sql
from core.encryption_handler import decrypt
from core.config_manager import get_db_config

def get_all_applicants_with_cv():
    DB_CONFIG = get_db_config()
    if not DB_CONFIG:
        print("Error: File konfigurasi 'config.ini' tidak ditemukan atau kosong.")
        print("Harap jalankan 'src/load_data.py' terlebih dahulu untuk membuat file konfigurasi.")
        return []

    applicants = []
    try:
        connect = sql.connect(**DB_CONFIG)
        cursor = connect.cursor(dictionary=True)

        query = """
            SELECT 
                p.applicant_id as id,
                p.first_name, p.last_name, p.date_of_birth, p.address, p.phone_number,
                d.cv_path
            FROM ApplicantProfile p JOIN ApplicationDetail d ON p.applicant_id = d.applicant_id
        """
        cursor.execute(query)
        
        raw_applicants = cursor.fetchall()

        for row in raw_applicants:
            decrypted_row = {
                'id': row['id'],
                'first_name': decrypt(row['first_name']),
                'last_name': decrypt(row['last_name']),
                'date_of_birth': decrypt(row['date_of_birth']),
                'address': decrypt(row['address']),
                'phone_number': decrypt(row['phone_number']),
                'cv_path': row['cv_path']
            }
            
            decrypted_row['name'] = f"{decrypted_row['first_name']} {decrypted_row['last_name']}".strip()
            applicants.append(decrypted_row)

    except sql.Error as err:
        print(f"Database Error: {err}")
        return []

    finally:
        if 'connect' in locals() and connect.is_connected():
            cursor.close()
            connect.close()
            
    return applicants
