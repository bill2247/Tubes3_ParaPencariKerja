import customtkinter as ctk
from config import Theme

class WarningPopup(ctk.CTkToplevel):
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

class FlowLayoutFrame(ctk.CTkFrame):
    def __init__(self, *args, child_padx=0, child_pady=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_padx = child_padx
        self.child_pady = child_pady
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event=None):
        self.update_idletasks()
        
        max_width = self.winfo_width()
        if max_width <= 1: return 

        current_x = 0
        current_y = 0
        row_height = 0

        children = self.winfo_children()
        for child in children:
            child.update_idletasks()
            width = child.winfo_reqwidth()
            height = child.winfo_reqheight()
            
            # Jika widget tidak muat di baris saat ini, pindah ke baris baru
            if current_x + width > max_width and current_x > 0:
                current_y += row_height + self.child_pady
                current_x = 0
                row_height = 0
            
            child.place(x=current_x, y=current_y)
            
            current_x += width + self.child_padx
            if height > row_height:
                row_height = height
        
        required_height = current_y + row_height
        self.configure(height=required_height)


class CVCard(ctk.CTkFrame):
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
