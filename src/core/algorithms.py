import os
import re
from collections import deque

# --- Exact Match Algorithms ---

def kmp_search(text, pattern):
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
    def bad_char_heuristic(string, size):
        bad_char = {}
        for i in range(size):
            bad_char[string[i]] = i
        return bad_char

    def find_first_match_in_segment(text_segment, pat, bad_char_table):
        m = len(pat)
        n = len(text_segment)
        if m > n:
            return -1

        i = m - 1
        j = m - 1

        while i < n:
            if pat[j] == text_segment[i]:
                if j == 0:
                    return i
                else:
                    i -= 1
                    j -= 1
            else:
                # Jika karakter tidak ada di tabel, defaultnya adalah -1.
                lo = bad_char_table.get(text_segment[i], -1)
                i = i + m - min(j, 1 + lo)
                j = m - 1
        
        return -1

    # Bagian utama: loop untuk mencari dan menghitung semua kecocokan.
    m = len(pattern)
    n = len(text)
    if m == 0 or n == 0 or m > n:
        return 0

    bad_char = bad_char_heuristic(pattern, m)
    count = 0
    current_pos = 0

    while current_pos <= n - m:
        match_pos = find_first_match_in_segment(text[current_pos:], pattern, bad_char)
        
        if match_pos != -1:
            count += 1
            current_pos += match_pos + 1
        else:
            break
            
    return count

class trie_node:
    def __init__(self):
        self.children = {} 
        self.output = []
        self.failure = None
                

# --- Implementasi Aho-Corasick ---
class TrieNode:
    def __init__(self):
        self.children = {} 
        self.output = []
        self.failure = None

def aho_corasick_search(text, patterns):
    # 1. Build Trie
    root = TrieNode()
    for kw in patterns:
        node = root
        for char in kw:
            node = node.children.setdefault(char, TrieNode())
        node.output.append(kw)

    # 2. Build Failure Links
    queue = deque()
    for node in root.children.values():
        node.failure = root
        queue.append(node)
    
    while queue:
        current_node = queue.popleft()
        for char, child_node in current_node.children.items():
            fail_node = current_node.failure
            while char not in fail_node.children and fail_node is not root:
                fail_node = fail_node.failure
            
            if char in fail_node.children:
                child_node.failure = fail_node.children[char]
            else:
                child_node.failure = root
            
            child_node.output.extend(child_node.failure.output)
            queue.append(child_node)

    # 3. Search Text
    found_counts = {kw: 0 for kw in patterns}
    node = root
    for char in text:
        while char not in node.children and node is not root:
            node = node.failure
        
        if char in node.children:
            node = node.children[char]
        
        for kw in node.output:
            found_counts[kw] += 1
            
    return found_counts

# --- Fuzzy Match & Regex Algorithms ---

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions, deletions, substitutions = previous_row[j + 1] + 1, current_row[j] + 1, previous_row[j] + (c1 != c2)
            insertions, deletions, substitutions = previous_row[j + 1] + 1, current_row[j] + 1, previous_row[j] + (c1 != c2)
            insertions, deletions, substitutions = previous_row[j + 1] + 1, current_row[j] + 1, previous_row[j] + (c1 != c2)
            insertions, deletions, substitutions = previous_row[j + 1] + 1, current_row[j] + 1, previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def find_fuzzy_matches(text, pattern, threshold=1):
    count = 0
    words_in_text = set(re.findall(r'\b\w+\b', text))
    for word in words_in_text:
        if levenshtein_distance(word, pattern) <= threshold:
            count += 1 
    return count

def extract_details_with_regex(full_cv_text):
    text = re.sub(r' +', ' ', full_cv_text).strip()
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  
    details = {"summary": "", "skills": [], "job_history": [], "education": []}

    # --- Ekstrak Summary ---
    summary_match = re.search(r'summary\s*(.*?)(?=highlights|skills|experience|education|work history)', text, re.IGNORECASE)
    if summary_match:
        details["summary"] = summary_match.group(1).strip()

    # --- Ekstrak Skills (ambil blok saja tanpa dipecah) ---
    # skills_match = re.search(r'(skills|highlights)\s*(.*?)(?=experience|education|summary|work history)', text, re.IGNORECASE)
    if not details["skills"]:
        fallback_skills_match = re.search(r'(?:accomplishments|strengths|capabilities)\s*(.*?)(?=experience|education|summary|work history)', text, re.IGNORECASE)
        if fallback_skills_match:
            block = fallback_skills_match.group(1).strip()
            details["skills"] = [block] if block else []

    # --- Ekstrak Job History ---
    job_matches = re.findall(
        r'(\d{2}/\d{4}\s*(?:to|-)?\s*\d{2}/\d{4}|\d{6}|\w+\s+\d{4}\s*(?:to|-)?\s*\w+\s+\d{4})\s*company name\s*city\s*,?\s*state\s*(.*?)\s*(?=\d{2}/\d{4}|company name|education|$)',
        text,
        re.IGNORECASE
    )
    for date_str, after_text in job_matches:
        if re.match(r'\d{6}', date_str):
            month = date_str[:2]
            year = date_str[2:]
            date_str = f"{month}/{year}"
        title_match = re.search(r'([A-Za-z\s/&\-]{3,})', after_text.strip())
        # title_match = re.search(r'(?:Company Name\s+.*?)([A-Z][a-zA-Z\s/&\-]+?)(?=\s*\d{2}/\d{4}|\s*\b\w+\s+\d{4})', entry, re.IGNORECASE)
        # title_match = re.search(r'(chef|cook|line cook|food service cook|supervisor|prep chef|server)', after_text, re.IGNORECASE)
        title = title_match.group(1).title() if title_match else "Unknown"
        details["job_history"].append({
            "title": title,
            "company": "Company Name",
            "dates": date_str
        })

    # --- Ekstrak Education ---
    edu_match = re.search(r'education\s*(.*)', text, re.IGNORECASE)
    if edu_match:
        block = edu_match.group(1).strip()
        date_match = re.search(r'(\d{4})', block)
        # major_match = re.search(r'(?:diploma\s*:|degree\s*(?:in)?|courses\s*in|major\s*in)?\s*([a-zA-Z ,&\-]+)', block, re.IGNORECASE)
        major_match = re.search(r'(?:diploma\s*:\s*|degree in\s*)([a-zA-Z ,&]+)', block, re.IGNORECASE)
        institution_match = re.search(r'([A-Z][\w\s,&\-]+(?:university|institute|college|academy|school|polytechnic|center|centre|faculty|campus))', block, re.IGNORECASE)
        
        if date_match:
            details["education"].append({
                "major": major_match.group(1).strip() if major_match else "",
                "institution": institution_match.group(1).strip() if institution_match else "",
                "dates": date_match.group(1)
            })

    return details
