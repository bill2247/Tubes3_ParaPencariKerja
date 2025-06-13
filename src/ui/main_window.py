import customtkinter as ctk
from tkinter import font
import webbrowser
import os

from config import Theme
from ui.widgets import WarningPopup, CVCard
from ui.summary_window import CVSummaryWindow
from core import search_handler, algorithms

class App(ctk.CTk):
    """Kelas utama aplikasi CV Analyzer."""
    def __init__(self):
        super().__init__()
        self.title("CV Analyzer App by paraPencariKerja")
        self.geometry("800x750")
        self.configure(fg_color=Theme.PARCHMENT)
        self._load_fonts()
        self.center_window()
        self._create_widgets()
        
        self.execution_time_label.configure(text="Masukkan kriteria pencarian dan tekan Search.")
        self.search_results_data = {}

        # Membuat satu instance jendela summary yang akan digunakan kembali
        self.summary_window = CVSummaryWindow(self)

    def _load_fonts(self):
        try:
            fonts = {"36": 36, "15": 15, "13": 13, "24": 24, "16": 16, "18": 18, "20": 20}
            for _, size in fonts.items():
                font.Font(family=Theme.FONT_FAMILY, size=size, weight="bold")
        except Exception as e:
            print(f"Peringatan: Font '{Theme.FONT_FAMILY}' tidak dapat dimuat. Error: {e}")
            Theme.FONT_FAMILY = "Arial"

    def center_window(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x, y = (self.winfo_screenwidth() - w) // 2, (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y-30}')

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))
        ctk.CTkLabel(header_frame, text="CV Analyzer App", font=(Theme.FONT_FAMILY, 36, "bold"), text_color=Theme.RICH_BLACK).pack()
        ctk.CTkLabel(header_frame, text="By paraPencariKerja", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).pack()
        
        self._create_input_controls(main_frame)

        results_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, pady=(10,0))
        ctk.CTkLabel(results_frame, text="Results", font=(Theme.FONT_FAMILY, 24, "bold"), text_color=Theme.RICH_BLACK).pack()
        self.execution_time_label = ctk.CTkLabel(results_frame, text="", font=(Theme.FONT_FAMILY, 13), text_color=Theme.TEAL)
        self.execution_time_label.pack(pady=(0, 10))
        self.scrollable_results_frame = ctk.CTkScrollableFrame(results_frame, fg_color="transparent")
        self.scrollable_results_frame.pack(fill="both", expand=True)
        self.scrollable_results_frame.grid_columnconfigure((0, 1), weight=1)
    
    def _create_input_controls(self, parent):
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Keyword:", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.keyword_entry = ctk.CTkEntry(input_frame, font=(Theme.FONT_FAMILY, 15), fg_color=Theme.ASH_GRAY, text_color=Theme.TEAL, placeholder_text="React, Express, HTML", border_width=0, height=35, corner_radius=8)
        self.keyword_entry.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(input_frame, text="Search Algorithm:", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.algo_combobox = ctk.CTkComboBox(input_frame, values=["KMP", "BM", "AC"], font=(Theme.FONT_FAMILY, 15), fg_color=Theme.ASH_GRAY, text_color=Theme.TEAL, border_width=0, height=35, corner_radius=8, state="readonly", button_color=Theme.TEAL, button_hover_color=Theme.CAMBRIDGE_BLUE)
        self.algo_combobox.set("Select Algorithm")
        self.algo_combobox.grid(row=1, column=1, sticky="ew", pady=(10, 0))

        ctk.CTkLabel(input_frame, text="Top Matches:", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.top_matches_entry = ctk.CTkEntry(input_frame, font=(Theme.FONT_FAMILY, 15), fg_color=Theme.ASH_GRAY, text_color=Theme.TEAL, placeholder_text="e.g., 10", border_width=0, height=35, corner_radius=8)
        self.top_matches_entry.insert(0, "3")
        self.top_matches_entry.grid(row=2, column=1, sticky="ew", pady=(10, 0))

        ctk.CTkButton(parent, text="Search", font=(Theme.FONT_FAMILY, 15, "bold"), fg_color=Theme.CAMBRIDGE_BLUE, text_color=Theme.PARCHMENT, hover_color=Theme.TEAL, height=40, corner_radius=8, command=self._on_search_click).pack(fill="x", ipady=5, pady=(20, 0))

    def _on_search_click(self):
        if not self.keyword_entry.get().strip(): WarningPopup(self, "Kolom 'Keyword' tidak boleh kosong."); return
        if self.algo_combobox.get() == "Select Algorithm": WarningPopup(self, "Silakan pilih 'Search Algorithm'."); return
        top_n_str = self.top_matches_entry.get().strip()
        try:
            top_n = int(top_n_str)
            if not (1 <= top_n <= 100): WarningPopup(self, "'Top Matches' harus angka antara 1 dan 100."); return
        except ValueError: WarningPopup(self, "'Top Matches' harus berupa angka."); return
        
        keywords_str = self.keyword_entry.get().strip()
        algorithm_choice = self.algo_combobox.get()
        
        self.execution_time_label.configure(text="Mencari... Harap tunggu...")
        self.update_idletasks()

        self.search_results_data = search_handler.perform_search(keywords_str, algorithm_choice, top_n)
        self._update_ui_with_results(self.search_results_data)

    def _update_ui_with_results(self, data):
        for widget in self.scrollable_results_frame.winfo_children(): widget.destroy()

        times = data.get("times", {})
        scanned_count = data.get("scanned_cv_count", 0)

        exact_text = f"Exact match: Scanned {scanned_count} CVs in {times.get('exact', 0)}ms"
        fuzzy_time = times.get('fuzzy', 0)
        
        full_text = f"{exact_text}\nFuzzy match: Scanned {scanned_count} CVs in {fuzzy_time}ms" if fuzzy_time > 0 else exact_text
        self.execution_time_label.configure(text=full_text)
        
        if not data.get("results"):
            ctk.CTkLabel(self.scrollable_results_frame, text="Tidak ada hasil yang ditemukan.", font=(Theme.FONT_FAMILY, 15)).pack(pady=20)
            return

        # --- PERBAIKAN DI SINI ---
        # Mengembalikan logika untuk menggunakan .grid()
        for i, cv_data in enumerate(data.get("results")):
            card = CVCard(self.scrollable_results_frame, cv_data,
                          summary_command=lambda d=cv_data: self._open_summary_window(d),
                          view_cv_command=lambda p=cv_data.get("cv_path"): self._open_cv_pdf(p))
            
            # Menghitung baris dan kolom untuk tata letak 2 kolom
            row = i // 2
            col = i % 2
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def _open_summary_window(self, cv_data):
        full_cv_text = search_handler.read_cv_text(cv_data['cv_path'])
        
        if not full_cv_text:
            WarningPopup(self, "Tidak dapat membaca konten dari file CV.")
            return

        print("Mengekstrak detail dengan Regex...")
        regex_details = algorithms.extract_details_with_regex(full_cv_text)
        print(full_cv_text)
        cv_data.update(regex_details)
        print(cv_data)
        
        self.summary_window.show(cv_data)

    def _open_cv_pdf(self, cv_path):
        if not cv_path:
            WarningPopup(self, "Path CV tidak ditemukan untuk kandidat ini."); return
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(base_dir)
            full_path = os.path.join(root_dir, 'data', cv_path)
            webbrowser.open(f'file://{os.path.realpath(full_path)}')
        except Exception as e:
            WarningPopup(self, f"Gagal membuka file CV.\nError: {e}")
