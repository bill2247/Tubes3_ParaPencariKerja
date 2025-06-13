import re

# --- Exact Match Algorithms ---

def kmp_search(text, pattern):
    """
    Mencari semua kemunculan pattern dalam text menggunakan algoritma KMP.
    Mengembalikan jumlah kemunculan.
    """
    def compute_lps_array(pat, M, lps):
        length = 0
        lps[0] = 0
        i = 1
        while i < M:
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length-1]
                else:
                    lps[i] = 0
                    i += 1

    M = len(pattern)
    N = len(text)
    if M == 0 or N == 0 or M > N:
        return 0

    lps = [0] * M
    compute_lps_array(pattern, M, lps)
    
    i = 0  # index for text
    j = 0  # index for pattern
    count = 0
    while i < N:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == M:
            count += 1
            j = lps[j-1]
        elif i < N and pattern[j] != text[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return count


def boyer_moore_search(text, pattern):
    """
    Mencari semua kemunculan pattern dalam text menggunakan algoritma Boyer-Moore.
    Logika pencarian disesuaikan dari contoh Java, dimodifikasi untuk menghitung semua
    kemunculan dan diperbaiki untuk menangani karakter non-ASCII (Unicode).
    """
    def bad_char_heuristic(string, size):
        # PERBAIKAN: Menggunakan dictionary untuk menangani semua karakter (Unicode).
        bad_char = {}
        for i in range(size):
            # Kunci adalah karakter itu sendiri, bukan nilai ord().
            bad_char[string[i]] = i
        return bad_char

    def find_first_match_in_segment(text_segment, pat, bad_char_table):
        """Menemukan kecocokan pertama di dalam segmen teks yang diberikan."""
        m = len(pat)
        n = len(text_segment)
        if m > n:
            return -1

        i = m - 1
        j = m - 1

        while i < n:
            if pat[j] == text_segment[i]:
                if j == 0:
                    return i
                else:
                    i -= 1
                    j -= 1
            else:
                # PERBAIKAN: Menggunakan .get() untuk lookup yang aman pada dictionary.
                # Jika karakter tidak ada di tabel, defaultnya adalah -1.
                lo = bad_char_table.get(text_segment[i], -1)
                i = i + m - min(j, 1 + lo)
                j = m - 1
        
        return -1

    # Bagian utama: loop untuk mencari dan menghitung semua kecocokan.
    m = len(pattern)
    n = len(text)
    if m == 0 or n == 0 or m > n:
        return 0

    bad_char = bad_char_heuristic(pattern, m)
    count = 0
    current_pos = 0

    while current_pos <= n - m:
        match_pos = find_first_match_in_segment(text[current_pos:], pattern, bad_char)
        
        if match_pos != -1:
            count += 1
            current_pos += match_pos + 1
        else:
            break
            
    return count



def aho_corasick_search(text, patterns):
    """Placeholder untuk algoritma Aho-Corasick (Bonus)."""
    # Implementasi Aho-Corasick akan ada di sini
    print("Aho-Corasick belum diimplementasikan.")
    return 0


# --- Fuzzy Match & Regex Algorithms ---

def levenshtein_distance(s1, s2):
    """Menghitung Levenshtein distance antara dua string."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]

def find_fuzzy_matches(text, pattern, threshold=1):
    """
    Mencari kata dalam teks yang mirip dengan pattern berdasarkan Levenshtein.
    Threshold default adalah 1, untuk mentolerir satu typo.
    """
    count = 0
    # Memecah teks menjadi kata-kata unik untuk efisiensi
    words_in_text = set(re.findall(r'\b\w+\b', text))
    for word in words_in_text:
        if levenshtein_distance(word, pattern) <= threshold:
            # Ini hanya menghitung sekali per kata unik yang cocok.
            # Untuk menghitung setiap kemunculan, Anda perlu iterasi teks asli.
            # Namun, untuk tujuan pemeringkatan, ini seringkali cukup.
            count += 1 
    return count

def extract_details_with_regex(full_cv_text):
    """
    Mengekstrak detail dari teks CV menggunakan Regex Heuristik yang dilatih
    berdasarkan sampel CV yang diberikan.
    """
    text = re.sub(r' +', ' ', full_cv_text).strip()
    
    details = {"skills": [], "job_history": [], "education": []}
    
    # Kumpulan judul bagian yang mungkin, diperluas dari sampel
    section_keywords = [
        'skills', 'keahlian', 'core qualifications', 'affiliations',
        'work history', 'experience', 'riwayat pekerjaan',
        'education', 'pendidikan', 'riwayat pendidikan'
    ]
    
    # Membuat satu pola Regex besar untuk menemukan batas antar bagian
    # Ini adalah kunci untuk memisahkan konten dengan benar
    section_boundary_pattern = r'\n\s*(?:' + '|'.join(section_keywords) + ')'

    # --- 1. Ekstraksi Skills ---
    try:
        # Pola: Cari "skills" (atau variasinya), lalu ambil semua teks (.*?)
        # sampai menemukan batas bagian berikutnya (?=...) atau akhir teks ($)
        skills_pattern = r"(?i)(?:skills|core qualifications|keahlian|affiliations)\s*:?\s*(.*?)(?=" + section_boundary_pattern + "|$)"
        match = re.search(skills_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            skills_block = match.group(1).strip()
            # Membersihkan dan memisahkan skills
            # Mencoba memisahkan dengan koma atau baris baru
            potential_skills = re.split(r',|\n', skills_block)
            cleaned_skills = []
            for skill in potential_skills:
                # Menghapus karakter non-alfanumerik di awal/akhir dan kata-kata umum
                s = re.sub(r'^\W+|\W+$', '', skill.strip()).strip()
                if s and len(s) > 1 and s.lower() not in ['and', 'etc']:
                    cleaned_skills.append(s)
            details['skills'] = list(dict.fromkeys(cleaned_skills)) # Hapus duplikat
    except Exception as e:
        print(f"Regex error in skills: {e}")

    # --- 2. Ekstraksi Education ---
    try:
        edu_pattern = r"(?i)(?:education|pendidikan)\s*:?\s*(.*?)(?=" + section_boundary_pattern + "|$)"
        match = re.search(edu_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            edu_block = match.group(1).strip()
            # Memisahkan setiap entri pendidikan (diasumsikan dipisah oleh baris kosong)
            entries = re.split(r'\n\s*\n|\bcompany name\b', edu_block, flags=re.IGNORECASE)
            for entry in entries:
                if not entry.strip(): continue
                lines = [line.strip() for line in entry.split('\n') if line.strip()]
                if not lines: continue
                
                major = lines[0]
                institution = ""
                dates = ""

                # Mencoba menemukan institusi dan tanggal di baris berikutnya
                if len(lines) > 1:
                    institution = lines[1]
                if len(lines) > 2:
                    # Cek jika baris mengandung tahun
                    if re.search(r'\b\d{4}\b', lines[2]):
                        dates = lines[2]
                    else:
                        institution += " " + lines[2] # Gabungkan jika bukan tanggal
                
                details['education'].append({"major": major, "institution": institution, "dates": dates})
    except Exception as e:
        print(f"Regex error in education: {e}")

    # --- 3. Ekstraksi Job History ---
    try:
        job_pattern = r"(?i)(?:work history|experience|riwayat pekerjaan)\s*:?\s*(.*?)(?=" + section_boundary_pattern + "|$)"
        match = re.search(job_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            job_block = match.group(1).strip()
            # Memisahkan entri pekerjaan, seringkali dipisahkan oleh 'company name' atau baris kosong
            entries = re.split(r'\n\s*\n|\bcompany name\b', job_block, flags=re.IGNORECASE)
            for entry in entries:
                if not entry.strip(): continue
                lines = [line.strip() for line in entry.split('\n') if line.strip()]
                if not lines: continue

                title = lines[0]
                dates = ""
                desc = ""

                # Mencoba mengekstrak tanggal dari judul atau baris kedua
                date_match = re.search(r'(\d{2}/\d{4}\s*to\s*\d{2}/\d{4}|\w+\s*\d{4}\s*to\s*\w+\s*\d{4})', entry, re.IGNORECASE)
                if date_match:
                    dates = date_match.group(1)
                    # Hapus tanggal dari judul jika ada
                    title = title.replace(dates, '').strip(', ')
                
                # Sisa baris dianggap sebagai deskripsi
                desc_lines = lines[1:]
                desc = " ".join(desc_lines).replace(dates, '').strip()

                details['job_history'].append({"title": title, "dates": dates, "desc": desc})
    except Exception as e:
        print(f"Regex error in job history: {e}")

    # Jika tidak ada yang terekstrak, kembalikan placeholder
    if not details["skills"] and not details["education"] and not details["job_history"]:
        return {"skills": ["Not Found via Regex"], "job_history": [], "education": []}

    return details