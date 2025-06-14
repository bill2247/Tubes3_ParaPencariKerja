import time
import os
import fitz  # PyMuPDF
from core import algorithms
from core.db_connector import get_all_applicants_with_cv

def read_cv_text(cv_path):
    """Membaca seluruh teks dari file PDF yang diberikan."""
    try:
        # Menentukan path absolut dari root proyek
        base_dir = os.path.dirname(os.path.abspath(__file__)) # /path/to/project/src/core
        root_dir = os.path.dirname(os.path.dirname(base_dir)) # /path/to/project
        full_path = os.path.join(root_dir, 'data', cv_path)
        
        if not os.path.exists(full_path):
            print(f"Peringatan: File CV tidak ditemukan di '{full_path}'")
            return ""
            
        doc = fitz.open(full_path)
        text = "".join(page.get_text() for page in doc)
        # Normalisasi teks: lowercase dan hapus spasi berlebih
        return " ".join(text.lower().split())
    except Exception as e:
        print(f"Error saat membaca CV {cv_path}: {e}")
        return ""

def perform_search(keywords_str, algorithm_choice, top_n):
    """
    Fungsi utama untuk mengorkestrasi seluruh proses pencarian.
    """
    # Normalisasi input keywords dari pengguna
    keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
    if not keywords:
        return {"times": {}, "results": []}

    # 1. Ambil data pelamar dari DB
    all_applicants = get_all_applicants_with_cv()
    num_scanned_cvs = len(all_applicants) # Menghitung jumlah total CV
    if not all_applicants:
        return {"times": {}, "results": [], "scanned_cv_count": 0}

    # Pilih fungsi pencarian berdasarkan pilihan UI
    search_function = {
        "KMP": algorithms.kmp_search,
        "BM": algorithms.boyer_moore_search,
        "AC": algorithms.aho_corasick_search  # Placeholder untuk bonus
    }.get(algorithm_choice, algorithms.kmp_search)  # Default ke KMP jika tidak valid

    # 2. Siklus Exact Match
    start_time_exact = time.time()
    search_results = {}
    unmatched_keywords = set(keywords)

    for applicant in all_applicants:
        cv_text = read_cv_text(applicant['cv_path'])
        if not cv_text:
            continue

        applicant_id = applicant['id']
        search_results[applicant_id] = {'applicant_data': applicant, 'score': 0, 'matched_keywords': {}}
        
        if algorithm_choice == "AC":
            counts = search_function(cv_text, keywords)  # dict of count (int)
            for kw, count in counts.items():
                if count > 0:
                    search_results[applicant_id]['matched_keywords'][kw] = count
                    # Jika keyword ditemukan, hapus dari set unmatched
                    if kw in unmatched_keywords:
                        unmatched_keywords.remove(kw)
                        
        else:
            for kw in keywords:
                count = search_function(cv_text, kw)
                if count > 0:
                    search_results[applicant_id]['matched_keywords'][kw] = count
                    # Jika keyword ditemukan, hapus dari set unmatched
                    if kw in unmatched_keywords:
                        unmatched_keywords.remove(kw)

    end_time_exact = time.time()
    cv_cocok_saat_ini = sum(1 for res in search_results.values() if res['matched_keywords'])

    # 3. Siklus Fuzzy Match
    start_time_fuzzy = time.time()
    fuzzy_match_performed = False
    if cv_cocok_saat_ini < top_n and unmatched_keywords:
        fuzzy_match_performed = True
        for applicant_id in search_results:
            result = search_results[applicant_id]
            cv_text = read_cv_text(result['applicant_data']['cv_path'])
            if not cv_text: continue
            
            for kw in list(unmatched_keywords):
                count = algorithms.find_fuzzy_matches(cv_text, kw, threshold=2)
                if count > 0:
                    fuzzy_key = f"{kw} (fuzzy)"
                    result['matched_keywords'][fuzzy_key] = count
    end_time_fuzzy = time.time()
    
    # 4. Kalkulasi Skor & Ranking
    for result in search_results.values():
        score = len(result['matched_keywords'])
        total_occurrences = sum(result['matched_keywords'].values())
        result['score'] = score * 10 + total_occurrences

    sorted_results = sorted(search_results.values(), key=lambda x: (x['score'], x['applicant_data']['name']), reverse=True)
    top_results = sorted_results[:top_n]
    
    # 5. Format hasil akhir untuk UI
    final_output = {
        "times": {
            "exact": int((end_time_exact - start_time_exact) * 1000),
            "fuzzy": int((end_time_fuzzy - start_time_fuzzy) * 1000) if fuzzy_match_performed else 0
        },
        "results": [],
        "scanned_cv_count": num_scanned_cvs # Menambahkan jumlah CV yang dipindai
    }

    for result in top_results:
        if result['score'] > 0:
            applicant_data = result['applicant_data']
            formatted_keywords = [f"{kw}: {count} occurence(s)" for kw, count in result['matched_keywords'].items()]
            final_output["results"].append({
                "id": applicant_data['id'],
                "name": applicant_data['name'],
                "matches": len(result['matched_keywords']),
                "matched_keywords": formatted_keywords,
                "cv_path": applicant_data['cv_path'],
                "birthdate": str(applicant_data.get('date_of_birth', 'N/A')),
                "address": applicant_data.get('address', 'N/A'),
                "phone": applicant_data.get('phone_number', 'N/A'),
                "skills": [], "job_history": [], "education": []
            })
            
    return final_output
