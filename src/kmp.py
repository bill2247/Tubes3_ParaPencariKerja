import mysql.connector as sql
import fitz
import os

def extract_pdf(path):
    """Mengesktrak teks CV PDF menjadi string."""
    with open(path, "rb") as f:
        pdf_bytes = f.read()

    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""

    for i, page in enumerate(document):
        text += page.get_text()

    text_low = text.lower()
    text_long = " ".join(text_low.split())

    return text, text_long

def border(pattern):
    """Membuat array fungsi border."""
    b = [0 for _ in range(len(pattern)-1)]
    m = len(pattern)-1
    j = 0
    i = 1

    while (i < m):
        if (pattern[j] == pattern[i]):
            # character match
            b[i] = j + 1
            i += 1
            j += 1
        elif (j > 0):
            j = b[j-1]
        else:
            b[i] = 0
            i += 1
    
    return b
            
def kmp(text, pattern):
    """Implementasi algoritma KMP."""
    n = len(text)
    m = len(pattern)

    b = border(pattern)

    i = 0
    j = 0

    counts = 0
    while (i < n):
        if (pattern[j] == text[i]):
            if (j == m - 1):
                counts += 1
                j = 0
            i += 1
            j += 1
        elif (j > 0):
            j = b[j-1]
        else: 
            i += 1
    
    if counts > 0:
        return counts
    return -1
 
def main():
    """Fungsi utama untuk menjalankan pencarian dengan algoritma KMP"""
    connect = sql.connect(
        host="localhost",
        user="root",
        password="lagrange",
        database="cv_application"
    )

    cursor = connect.cursor()
    cursor.execute("""
                SELECT 
                        ad.detail_id, ad.application_role, ad.cv_path,
                        ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number
                FROM ApplicationDetail ad
                JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
    """)

    keywords = ["javascript", "python"]

    data_all = cursor.fetchall()

    found = {}

    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    data_dir = os.path.join(project_root, "data")

    print("Mencari...")
    # exact matching
    for detailed_id, role, cv_path, fname, lname, birth, address, phone in data_all:
        personal_info = f"{fname} {lname} {birth} {address} {phone}".lower()

        _, cv_text = extract_pdf(os.path.join(data_dir, cv_path))

        keyword_dict = {}
        for kw in keywords:
            found_in_personal = kmp(personal_info, kw.lower())
            found_in_cv = kmp(cv_text, kw.lower())

            # Cek keberadaan keyword
            if found_in_personal == -1 and found_in_cv != -1:
                keyword_dict[kw] = found_in_cv
            elif found_in_personal != -1 and found_in_cv == -1:
                keyword_dict[kw] = found_in_personal 
            elif found_in_personal != -1 and found_in_cv != -1:
                keyword_dict[kw] = found_in_personal + found_in_cv
            elif found_in_personal == -1 and found_in_cv == -1:
                keyword_dict[kw] = 0

        for val in keyword_dict.values():
            if val != 0:
                cv = cv_path.split("/")[-1]
                found[cv] = keyword_dict
                break

    # Panggil fungsi fuzzy matching
    # if found == {}:


    # Mengurutkan hasil dari temuan terbanyak
    print("Hasil:")
    if found:
        # Urutkan dict berdasarkan hasil temuan terbanyak
        jumlah = {key: sum(list(val.values())) for key, val in found.items()}
        jumlah_sorted = dict(sorted(jumlah.items(), key=lambda item: item[1], reverse=True))
        found_sorted = {key: found[key] for key in jumlah_sorted.keys()}

        print("Kata kunci ditemukan.")
        print(found_sorted)
        
    else:
        print("Kata kunci tidak ditemukan.")

    cursor.close()
    connect.close()

if __name__ == "__main__":
    main()