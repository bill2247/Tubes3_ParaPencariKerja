import mysql.connector as sql
import os
from config import Theme  # Meskipun tidak digunakan, ini untuk konsistensi

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "lagrange",  # Ganti dengan password MySQL Anda
    "database": "cv_application"
}

def get_all_applicants_with_cv():
    """
    Mengambil semua data pelamar yang digabungkan dari ApplicantProfile dan ApplicationDetail.
    """
    applicants = []
    try:
        connect = sql.connect(**DB_CONFIG)
        cursor = connect.cursor(dictionary=True) # dictionary=True agar hasil seperti dict

        query = """
            SELECT 
                p.applicant_id as id,
                p.first_name,
                p.last_name,
                p.date_of_birth,
                p.address,
                p.phone_number,
                d.cv_path
            FROM 
                ApplicantProfile p
            JOIN 
                ApplicationDetail d ON p.applicant_id = d.applicant_id
        """
        cursor.execute(query)
        
        for row in cursor.fetchall():
            # Menggabungkan nama depan dan belakang
            row['name'] = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
            applicants.append(row)

    except sql.Error as err:
        print(f"Database Error: {err}")
        # Mengembalikan data dummy jika koneksi DB gagal agar UI tidak error
        from .data_manager import get_dummy_search_results
        return get_dummy_search_results().get("results", [])

    finally:
        if 'connect' in locals() and connect.is_connected():
            cursor.close()
            connect.close()
            
    return applicants
