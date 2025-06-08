import customtkinter as ctk
from config import Theme

class CVSummaryWindow(ctk.CTkToplevel):
    """Jendela pop-up untuk menampilkan detail lengkap dari sebuah CV."""
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data

        self.transient(parent)
        self.title(f"Summary: {self.data.get('name', 'N/A')}")
        self.geometry("600x700")
        self.configure(fg_color=Theme.PARCHMENT)
        self.resizable(False, False)
        
        parent.update_idletasks()
        parent_x, parent_y, w, h = parent.winfo_x(), parent.winfo_y(), parent.winfo_width(), parent.winfo_height()
        self.geometry(f"600x700+{parent_x + (w - 600) // 2}+{parent_y + (h - 700) // 2}")
        
        self._create_widgets()
        self.lift()
        self.grab_set()

    def _create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(main_frame, text="CV Summary", font=(Theme.FONT_FAMILY, 36, "bold"), text_color=Theme.RICH_BLACK).pack(pady=(10, 0))
        ctk.CTkLabel(main_frame, text="By paraPencariKerja", font=(Theme.FONT_FAMILY, 15), text_color=Theme.RICH_BLACK).pack(pady=(0, 20))

        info_box = ctk.CTkFrame(main_frame, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
        info_box.pack(fill="x", pady=10, ipady=10)
        ctk.CTkLabel(info_box, text=self.data.get("name", "N/A"), font=(Theme.FONT_FAMILY, 24, "bold"), text_color=Theme.PARCHMENT).pack(pady=(5,10))
        ctk.CTkLabel(info_box, text=f"Birthdate: {self.data.get('birthdate', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
        ctk.CTkLabel(info_box, text=f"Address: {self.data.get('address', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
        ctk.CTkLabel(info_box, text=f"Phone: {self.data.get('phone', 'N/A')}", font=(Theme.FONT_FAMILY, 15), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20, pady=(0,5))

        ctk.CTkLabel(main_frame, text="Skills:", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.RICH_BLACK).pack(anchor="w", pady=(20, 5), padx=5)
        skills_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        skills_frame.pack(fill="x", padx=5)
        for skill in self.data.get("skills", []):
            skill_pill = ctk.CTkButton(skills_frame, text=skill, fg_color=Theme.TEAL, text_color=Theme.PARCHMENT, font=(Theme.FONT_FAMILY, 13, "bold"), state="disabled", corner_radius=15)
            skill_pill.pack(side="left", padx=(0, 10), pady=5)
            
        ctk.CTkLabel(main_frame, text="Job History:", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.RICH_BLACK).pack(anchor="w", pady=(20, 5), padx=5)
        for job in self.data.get("job_history", []):
            job_box = ctk.CTkFrame(main_frame, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
            job_box.pack(fill="x", pady=5, ipady=5)
            ctk.CTkLabel(job_box, text=job.get("title", ""), font=(Theme.FONT_FAMILY, 18, "bold"), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
            ctk.CTkLabel(job_box, text=job.get("dates", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
            ctk.CTkLabel(job_box, text=job.get("desc", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT, wraplength=500, justify="left").pack(anchor="w", padx=20, pady=(0,5))

        ctk.CTkLabel(main_frame, text="Education:", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.RICH_BLACK).pack(anchor="w", pady=(20, 5), padx=5)
        for edu in self.data.get("education", []):
            edu_box = ctk.CTkFrame(main_frame, fg_color=Theme.CAMBRIDGE_BLUE, corner_radius=15)
            edu_box.pack(fill="x", pady=5, ipady=5)
            ctk.CTkLabel(edu_box, text=edu.get("major", ""), font=(Theme.FONT_FAMILY, 18, "bold"), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
            ctk.CTkLabel(edu_box, text=edu.get("institution", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20)
            ctk.CTkLabel(edu_box, text=edu.get("dates", ""), font=(Theme.FONT_FAMILY, 14), text_color=Theme.PARCHMENT).pack(anchor="w", padx=20, pady=(0,5))
