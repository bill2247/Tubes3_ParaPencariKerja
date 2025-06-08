from faker import Faker
import mysql.connector as sql
import fitz
import os
import random
SEED = 42
random.seed(SEED)
Faker.seed(SEED)

def generate_fake_data(length):
    id = [i for i in range(length)]
    faker = Faker()

    primer_key = {} # id: (first name, last name, date of birth, address, phone number)
    for i in range(len(id)):
        first_name = faker.first_name()
        last_name = faker.last_name()
        birth = faker.date_of_birth()
        address = faker.address()
        phone = faker.phone_number()

        primer_key[id[i]] = (first_name, last_name, birth, address, phone)

    return primer_key

def extract_pdf(path):
    with open(path, "rb") as f:
        pdf_bytes = f.read()

    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    for i, page in enumerate(document):
        text += page.get_text()
        if i == 0:
            role = text.strip().split('\n')[0]

    text_low = text.lower()
    text_long = " ".join(text_low.split())

    return role, text, text_long

def load(database, user, password, data, data2):
    connect = sql.connect(
        host="localhost",
        user=user,
        password=password
    )

    cursor = connect.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}") # cv_database
    cursor.execute(f"USE {database}")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ApplicantProfile (
            applicant_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) DEFAULT NULL,
            last_name VARCHAR(50) DEFAULT NULL,
            date_of_birth DATE DEFAULT NULL,
            address VARCHAR(255) DEFAULT NULL,
            phone_number VARCHAR(30) DEFAULT NULL
        )
""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ApplicationDetail (
            detail_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            applicant_id INT NOT NULL,
            application_role VARCHAR(200) DEFAULT NULL,
            cv_path TEXT,
            FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
        )
""")
    
    try:
        check_query = "SELECT applicant_id FROM ApplicantProfile WHERE first_name = %s AND last_name = %s AND phone_number = %s"
        cursor.execute(check_query, (data[0], data[1], data[4]))
        is_available = cursor.fetchone()

        if is_available:
            applicant_id = is_available[0]

        else:
            insert_applicant = "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_applicant, data)
            applicant_id = cursor.lastrowid

        insert_role = "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)"
        cursor.execute(insert_role, (applicant_id, data2[0], data2[1]))
        connect.commit()

    except sql.Error as err:
        connect.rollback()
        print(f"Error: {err}")

    finally:
        cursor.close()
        connect.close()

field = os.listdir("data/")

# bikin daftar customernya dulu
# nanti submit data nya satu satu (random pilih id/custumer) ke sql langsung sama cv nya
id_len = 400  # 1 orang bisa punya lebih dari 1 CV
primer_key = generate_fake_data(id_len)

print("Load data to MySQL...")
for i in range(len(field)): 
    fnames = os.listdir("data/"+field[i]+"/")
    random.Random(i+2).shuffle(fnames) # acak urutannya
    for j in range(20): # ambil 20 cv setiap bidang
        id = random.randint(0, id_len-1)  # ini untuk pilih applicant
        fname = fnames[j]

        role, _, _ = extract_pdf(f"data/{field[i]}/{fname}")
        role = f"{role}, {field[i]}"
        data2 = (role, fname)

        # masukan data id ke tabel A SQL, pindah ke tabel B, isi data cv ke tabel B. 
        # Apabila id sudah ada di tabel A, isi cv ke tabel B (relasional) 
        load("cv_application", "root", "lagrange", primer_key[id], data2)

print("Data loaded")
