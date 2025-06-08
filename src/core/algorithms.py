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
    Mengembalikan jumlah kemunculan.
    """
    def bad_char_heuristic(string, size):
        bad_char = [-1] * 256
        for i in range(size):
            bad_char[ord(string[i])] = i
        return bad_char

    m = len(pattern)
    n = len(text)
    if m == 0 or n == 0 or m > n:
        return 0
    
    bad_char = bad_char_heuristic(pattern, m)
    
    s = 0
    count = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        
        if j < 0:
            count += 1
            s += (m - bad_char[ord(text[s + m])] if s + m < n else 1)
        else:
            s += max(1, j - bad_char[ord(text[s + j])])
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
    """Mengekstrak detail dari teks CV menggunakan Regex (placeholder)."""
    # Implementasi Regex yang sebenarnya akan sangat kompleks dan perlu banyak pengujian.
    # Ini adalah placeholder yang mengembalikan data dummy untuk demonstrasi.
    details = {
        "skills": ["Python (from Regex)", "SQL (from Regex)", "Tableau (from Regex)"],
        "job_history": [{"title": "Data Analyst (from Regex)", "dates": "2020 - 2022", "desc": "Menganalisis set data besar untuk wawasan bisnis."}],
        "education": [{"major": "Statistics (from Regex)", "institution": "University of Life", "dates": "2016 - 2020"}]
    }
    return details
