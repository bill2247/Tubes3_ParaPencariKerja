import time
import os
import fitz
from core import algorithms
from core.db_connector import get_all_applicants_with_cv

def read_cv_text(cv_path):
    """
    Membaca seluruh teks dari file PDF. Dibuat lebih tangguh untuk menangani
    berbagai kemungkinan format path.
    """
    try:
        clean_path = cv_path.strip() if cv_path else ""
        if not clean_path:
            return ""

        if os.path.isabs(clean_path) and os.path.exists(clean_path):
            full_path = clean_path
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(base_dir))
            full_path = os.path.join(project_root, clean_path)

        if not os.path.exists(full_path):
            print(f"Peringatan: Gagal menemukan file CV. Path yang dicoba: '{full_path}'")
            return ""
            
        doc = fitz.open(full_path)
        text = "".join(page.get_text() for page in doc)
        return " ".join(text.lower().split())
    except Exception as e:
        print(f"Error saat memproses CV di path '{cv_path}': {e}")
        return ""

def perform_search(keywords_str, algorithm_choice, top_n):
    """Fungsi utama untuk mengorkestrasi seluruh proses pencarian."""
    keywords = [kw.strip().lower() for kw in keywords_str.split(',') if kw.strip()]
    if not keywords:
        return {"times": {}, "results": []}

    all_applicants = get_all_applicants_with_cv()
    num_scanned_cvs = len(all_applicants)
    if not all_applicants:
        return {"times": {}, "results": [], "scanned_cv_count": 0}

    start_time_exact = time.time()
    search_results = {}
    unmatched_keywords = set(keywords)

    for applicant in all_applicants:
        cv_text = read_cv_text(applicant.get('cv_path'))
        if not cv_text: continue
            
        applicant_id = applicant['id']
        search_results[applicant_id] = {'applicant_data': applicant, 'score': 0, 'matched_keywords': {}}

        # Logika dipisahkan berdasarkan algoritma
        if algorithm_choice == "AC":
            # Panggil Aho-Corasick sekali dengan SEMUA keywords
            all_counts = algorithms.aho_corasick_search(cv_text, keywords)
            for kw, count in all_counts.items():
                if count > 0:
                    search_results[applicant_id]['matched_keywords'][kw] = count
                    if kw in unmatched_keywords: unmatched_keywords.remove(kw)
        else:
            # Logika lama untuk KMP dan BM (pencarian satu per satu)
            search_function = {
                "KMP": algorithms.kmp_search,
                "BM": algorithms.boyer_moore_search
            }.get(algorithm_choice, algorithms.kmp_search)
            
            for kw in keywords:
                count = search_function(cv_text, kw)
                if count > 0:
                    search_results[applicant_id]['matched_keywords'][kw] = count
                    if kw in unmatched_keywords: unmatched_keywords.remove(kw)
    
    end_time_exact = time.time()

    cv_cocok_saat_ini = sum(1 for res in search_results.values() if res['matched_keywords'])
    start_time_fuzzy = time.time()
    fuzzy_match_performed = False
    if cv_cocok_saat_ini < top_n and unmatched_keywords:
        fuzzy_match_performed = True
        for applicant_id in search_results:
            result = search_results[applicant_id]
            cv_text = read_cv_text(result['applicant_data'].get('cv_path'))
            if not cv_text: continue
            
            for kw in list(unmatched_keywords):
                # Panggil fungsi fuzzy_search terpadu untuk semua kasus
                count = algorithms.fuzzy_search(cv_text, kw, threshold=2)
                if count > 0:
                    result['matched_keywords'][f"{kw} (fuzzy)"] = result.get(f"{kw} (fuzzy)", 0) + count

    end_time_fuzzy = time.time()

    for result in search_results.values():
        # Jika ada frasa dalam pencarian, skor hanya dihitung jika frasa itu cocok.
        contains_phrase = any(' ' in kw for kw in result['matched_keywords'])
        is_phrase_search = any(' ' in kw for kw in keywords)

        # Jika ini adalah pencarian frasa, tapi CV ini tidak cocok dengan frasa apapun, beri skor 0
        if is_phrase_search and not contains_phrase:
            result['score'] = 0
        else:
            score = len(result['matched_keywords'])
            total_occurrences = sum(result['matched_keywords'].values())
            result['score'] = score * 10 + total_occurrences

    sorted_results = sorted(search_results.values(), key=lambda x: (x['score'], x['applicant_data']['name']), reverse=True)
    top_results = sorted_results[:top_n]
    
    final_output = {
        "times": {
            "exact": int((end_time_exact - start_time_exact) * 1000),
            "fuzzy": int((end_time_fuzzy - start_time_fuzzy) * 1000) if fuzzy_match_performed else 0
        },
        "results": [],
        "scanned_cv_count": num_scanned_cvs
    }

    for result in top_results:
        if result['score'] > 0:
            applicant_data = result['applicant_data']
            
            # --- PERBAIKAN DI SINI ---
            # Memastikan path yang dikirim ke UI selalu absolut.
            original_path = applicant_data['cv_path']
            if os.path.isabs(original_path):
                final_path = original_path
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(base_dir))
                final_path = os.path.join(project_root, original_path)

            final_output["results"].append({
                "id": applicant_data['id'],
                "name": applicant_data['name'],
                "matches": len(result['matched_keywords']),
                "matched_keywords": [f"{kw}: {count} occurence(s)" for kw, count in result['matched_keywords'].items()],
                "cv_path": final_path, # Menggunakan path yang sudah dijamin absolut
                "birthdate": str(applicant_data.get('date_of_birth', 'N/A')),
                "address": applicant_data.get('address', 'N/A'),
                "phone": applicant_data.get('phone_number', 'N/A'),
                "skills": [], "job_history": [], "education": []
            })
    return final_output
