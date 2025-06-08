import customtkinter as ctk
from config import Theme

class WarningPopup(ctk.CTkToplevel):
    """Jendela pop-up untuk menampilkan pesan peringatan."""
    def __init__(self, parent, message):
        super().__init__(parent)
        self.transient(parent)
        self.title("Peringatan")
        self.geometry("350x150")
        self.configure(fg_color=Theme.PARCHMENT)
        self.resizable(False, False)
        
        parent.update_idletasks()
        parent_x, parent_y, w, h = parent.winfo_x(), parent.winfo_y(), parent.winfo_width(), parent.winfo_height()
        self.geometry(f"350x150+{parent_x + (w - 350) // 2}+{parent_y + (h - 150) // 2}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text=message, font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK, wraplength=320)
        label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ok_button = ctk.CTkButton(self, text="OK", font=(Theme.FONT_FAMILY, 13, "bold"), fg_color=Theme.CAMBRIDGE_BLUE, text_color=Theme.PARCHMENT, hover_color=Theme.TEAL, width=100, command=self.destroy)
        ok_button.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        self.lift()
        self.grab_set()

class CVCard(ctk.CTkFrame):
    """Widget kartu untuk menampilkan ringkasan hasil pencarian satu CV."""
    def __init__(self, parent, data, summary_command, view_cv_command):
        super().__init__(parent, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text=data.get("name", "N/A"), font=(Theme.FONT_FAMILY, 16, "bold"), text_color=Theme.PARCHMENT, anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text=f"{data.get('matches', 0)} Matches", font=(Theme.FONT_FAMILY, 16), text_color=Theme.PARCHMENT, anchor="e").grid(row=0, column=1, sticky="e")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        ctk.CTkLabel(body, text="Matched keyword", font=(Theme.FONT_FAMILY, 13), text_color=Theme.PARCHMENT, anchor="w").pack(anchor="w")
        for i, kw in enumerate(data.get("matched_keywords", []), 1):
            ctk.CTkLabel(body, text=f"{i}. {kw}", font=(Theme.FONT_FAMILY, 13), text_color=Theme.PARCHMENT, anchor="w").pack(anchor="w", padx=(10, 0))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)
        
        summary_button = ctk.CTkButton(footer, text="Summary", fg_color=Theme.ASH_GRAY, text_color=Theme.RICH_BLACK, hover_color=Theme.PARCHMENT, font=(Theme.FONT_FAMILY, 13, "bold"), width=80, command=summary_command)
        summary_button.grid(row=0, column=0, sticky="w")
        
        view_cv_button = ctk.CTkButton(footer, text="View CV", fg_color=Theme.ASH_GRAY, text_color=Theme.RICH_BLACK, hover_color=Theme.PARCHMENT, font=(Theme.FONT_FAMILY, 13, "bold"), width=80, command=view_cv_command)
        view_cv_button.grid(row=0, column=1, sticky="e")

