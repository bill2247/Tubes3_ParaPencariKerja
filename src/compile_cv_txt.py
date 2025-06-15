import os
import fitz # PyMuPDF
import random

def read_and_format_cv_text(full_path, category):
    try:
        if not os.path.exists(full_path):
            print(f"Peringatan: File tidak ditemukan di '{full_path}'")
            return ""
            
        doc = fitz.open(full_path)
        text = "".join(page.get_text() for page in doc)
        normalized_text = " ".join(text.lower().split())
        
        return f"**Contoh CV (Kategori: {category})**\n\n{normalized_text}\n\n---\n\n"
    
    except Exception as e:
        print(f"Error saat membaca file {full_path}: {e}")
        return ""

def compile_cv_samples():
    try:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        if not os.path.isdir(base_dir):
            print(f"Error: Direktori data tidak ditemukan di '{base_dir}'")
            return

        all_categories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        
        num_samples = min(5, len(all_categories))
        sampled_categories = random.sample(all_categories, num_samples)
        
        print(f"Mengambil sampel dari kategori: {', '.join(sampled_categories)}")
        
        combined_text = ""
        for category in sampled_categories:
            category_path = os.path.join(base_dir, category)
            cv_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
            
            if cv_files:
                random_cv_file = random.choice(cv_files)
                full_path_to_cv = os.path.join(category_path, random_cv_file)
                
                print(f"  -> Memproses: {category}/{random_cv_file}")
                combined_text += read_and_format_cv_text(full_path_to_cv, category)

        output_path = os.path.join(os.path.dirname(base_dir), "cv_samples_for_analysis.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
            
        print(f"\nProses selesai. Sampel CV telah disimpan di: {output_path}")

    except Exception as e:
        print(f"Terjadi error pada proses utama: {e}")


if __name__ == "__main__":
    compile_cv_samples()

