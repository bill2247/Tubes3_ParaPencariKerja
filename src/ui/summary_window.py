import customtkinter as ctk
from config import Theme
from ui.widgets import FlowLayoutFrame

class CVSummaryWindow(ctk.CTkToplevel):
    """
    Jendela pop-up yang dapat digunakan kembali dengan layout yang sepenuhnya dinamis.
    Memperbaiki ValueError dan AttributeError.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.configure(fg_color=Theme.PARCHMENT)
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self._create_permanent_structure()
        self.withdraw()

    def _update_wraplength(self, event, label):
        """Callback untuk mengatur wraplength label secara dinamis."""
        padding = 40
        wrap_width = event.width - padding
        if wrap_width > 0:
            label.configure(wraplength=wrap_width)

    def _create_permanent_structure(self):
        """Membuat struktur widget permanen hanya sekali."""
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))
        ctk.CTkLabel(header_frame, text="CV Summary", font=(Theme.FONT_FAMILY, 36, "bold"), text_color=Theme.RICH_BLACK).pack()
        ctk.CTkLabel(header_frame, text="By paraPencariKerja", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).pack()

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="ew")
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _populate_content(self, data):
        """Menghapus konten lama dan mengisi dengan data baru."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        info_box = ctk.CTkFrame(self.content_frame, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
        info_box.grid(row=0, column=0, sticky="ew", pady=10)
        info_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(info_box, text=data.get("name", "N/A"), font=(Theme.FONT_FAMILY, 24, "bold"), text_color=Theme.PARCHMENT).pack(pady=(10,10))
        ctk.CTkLabel(info_box, text=f"Birthdate: {data.get('birthdate', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
        # addr_label = ctk.CTkLabel(info_box, text=f"Address: {data.get('address', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT, justify="left")
        # addr_label.pack(anchor="w", padx=20, fill="x")
        # info_box.bind('<Configure>', lambda e, lbl=addr_label: self._update_wraplength(e, lbl))
        ctk.CTkLabel(info_box, text=f"Address: {data.get('address', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT, justify="left").pack(anchor="w", padx=20, pady=(0,10))
        ctk.CTkLabel(info_box, text=f"Phone: {data.get('phone', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20, pady=(0,10))
        
        ctk.CTkLabel(self.content_frame, text="Skills:", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.RICH_BLACK).grid(row=1, column=0, sticky="w", pady=(20, 5), padx=5)
        skills_container = FlowLayoutFrame(self.content_frame, fg_color="transparent", child_padx=10, child_pady=5)
        skills_container.grid(row=2, column=0, sticky="ew")
        self.populate_flow_layout(skills_container, data.get("skills", []))

        self._populate_section(self.content_frame, "Job History", data.get("job_history", []), start_row=3)
        self._populate_section(self.content_frame, "Education", data.get("education", []), start_row=5)

    def populate_flow_layout(self, container, items):
        """Menata item (skills) dalam layout yang mengalir (wrap)."""
        for item_text in items:
            # PERBAIKAN: padx dan pady dihapus dari konstruktor
            pill = ctk.CTkButton(container, text=item_text, fg_color=Theme.TEAL, text_color=Theme.PARCHMENT, font=(Theme.FONT_FAMILY, 13, "bold"), state="disabled", corner_radius=15)
            # .pack() digunakan di sini hanya untuk FlowLayoutFrame mendeteksi widget anak.
            # Penempatan sebenarnya dilakukan oleh .place() di dalam FlowLayoutFrame.
            pill.pack()

    def _populate_section(self, parent, title_text, items, start_row):
        """Membuat bagian untuk Job History atau Education."""
        ctk.CTkLabel(parent, text=f"{title_text}:", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.RICH_BLACK).grid(row=start_row, column=0, sticky="w", pady=(20, 5), padx=5)
        
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.grid(row=start_row + 1, column=0, sticky="ew")
        section_frame.grid_columnconfigure(0, weight=1)

        for item in items:
            item_box = ctk.CTkFrame(section_frame, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
            item_box.pack(fill="x", pady=5)
            item_box.grid_columnconfigure(0, weight=1)
            
            title_label = ctk.CTkLabel(item_box, text=item.get("title") or item.get("major", ""), font=(Theme.FONT_FAMILY, 18, "bold"), text_color=Theme.PARCHMENT, justify="left")
            title_label.pack(fill="x", anchor="w", padx=20, pady=(10,0))
            item_box.bind('<Configure>', lambda e, lbl=title_label: self._update_wraplength(e, lbl))
            
            if "institution" in item:
                inst_label = ctk.CTkLabel(item_box, text=item.get("institution", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT, justify="left")
                inst_label.pack(fill="x", anchor="w", padx=20)
                item_box.bind('<Configure>', lambda e, lbl=inst_label: self._update_wraplength(e, lbl), add='+')
                
            ctk.CTkLabel(item_box, text=item.get("dates", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
            
            if "desc" in item and item.get("desc"):
                desc_label = ctk.CTkLabel(item_box, text=item.get("desc", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT, justify="left")
                desc_label.pack(fill="x", anchor="w", padx=20, pady=(0,10))
                item_box.bind('<Configure>', lambda e, lbl=desc_label: self._update_wraplength(e, lbl), add='+')

    def show(self, data):
        """Mengisi dan menampilkan jendela dengan data baru."""
        self.title(f"Summary: {data.get('name', 'N/A')}")
        self.geometry("600x700")
        self._populate_content(data)
        self.parent.update_idletasks()
        parent_x, parent_y, w, h = self.parent.winfo_x(), self.parent.winfo_y(), self.parent.winfo_width(), self.parent.winfo_height()
        self.geometry(f"600x700+{parent_x + (w - 600) // 2}+{parent_y + (h - 700) // 2}")
        self.deiconify()
        self.lift()
        self.grab_set()

    def hide(self):
        """Menyembunyikan jendela dan melepaskan grab."""
        self.grab_release()
        self.withdraw()
