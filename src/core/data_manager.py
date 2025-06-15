def get_dummy_search_results():
    return {
        "times": {"exact": 700, "fuzzy": 600},
        "results": [
            {
                "id": 1,
                "name": "Sabilul Huda", 
                "matches": 4, 
                "matched_keywords": ["React: 1", "Express: 2", "HTML: 1"], 
                "cv_path": "DESIGNER/10276858.pdf", 
                "birthdate": "2003-10-05", 
                "address": "Cisitu Lama 11, Bandung", 
                "phone": "0811-1111-1111", 
                "skills": ["React", "Express", "HTML", "Python", "SQL"], 
                "job_history": [{"title": "CTO", "dates": "2023 - 2025", "desc": "Leading the organization's technology strategies and initiatives."}], 
                "education": [{"major": "Informatics Engineering", "institution": "(Institut Teknologi Bandung)", "dates": "2022 - 2026"}]
            },
            {
                "id": 2,
                "name": "Farhan Kebab", 
                "matches": 2, 
                "matched_keywords": ["Python: 3", "Django: 1"], 
                "cv_path": "ACCOUNTANT/11995833.pdf", 
                "birthdate": "2002-05-20", 
                "address": "Jl. Ganesha No. 10, Bandung", 
                "phone": "0812-3456-7890", 
                "skills": ["Python", "Django", "Flask", "MySQL", "PostgreSQL"], 
                "job_history": [{"title": "Backend Developer", "dates": "2021 - Present", "desc": "Developing scalable web applications and REST APIs for various clients."}], 
                "education": [{"major": "Computer Science", "institution": "(Universitas Indonesia)", "dates": "2020 - 2024"}]
            }
        ]
    }
