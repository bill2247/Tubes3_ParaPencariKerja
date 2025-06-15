# CV Analyzer App - An ATS-Based Recruitment Application

This application is an implementation of the final project for IF2211 Algorithm Strategies, serving as a simple Applicant Tracking System (ATS). The system is capable of scanning and analyzing a collection of CV documents in PDF format to find the most relevant candidates based on a set of keywords provided by the user. This application utilizes various pattern matching algorithms to perform both exact and fuzzy matching searches.

## Brief Explanation of Algorithms

This application uses several strategic algorithms to achieve its functionality:

* **Knuth-Morris-Pratt (KMP):** This algorithm is used as one of the options for exact pattern matching. KMP preprocesses the keyword to create a table (LPS array) that allows for intelligent shifts when a mismatch occurs. This avoids repeated comparisons on the text and improves search efficiency by scanning the text from left to right.

* **Boyer-Moore (BM):** This is the second option for exact pattern matching, which is often faster in practice. The uniqueness of the BM algorithm is that it starts its comparison from the rightmost character of the pattern. By using the *bad-character heuristic*, this algorithm can make large jumps across the text when a mismatch is found, significantly reducing the total number of required comparisons.

* **Aho-Corasick (AC):** Implemented as a bonus feature, this algorithm is the most efficient choice for searching for **multiple keywords simultaneously**. It builds a *Trie* data structure combined with *failure links*, allowing all keywords to be searched in just a single pass over the CV text.

* **Levenshtein Distance (Fuzzy Match):** This algorithm does not look for exact matches but instead measures the "similarity distance" between two words. It is conditionally activated to handle typos or word variations. If the distance between a keyword and a word in the CV is below a specified threshold, it is considered a match.

## Prerequisites

-   Python 3.8 or higher
-   A running MySQL or MariaDB Server instance
-   Tkinter GUI Toolkit

## Installation and Setup

Follow these steps to set up the project environment.

1.  **Setup System Dependencies:**

    Ensure that a MySQL/MariaDB server and Tkinter are installed on your system.

    **On Linux (Debian/Ubuntu based):**
    ```bash
    sudo apt-get update && sudo apt-get install -y python3-tk mysql-server
    ```
    **On Windows:**
    -   Ensure that during the Python installation from [python.org](https://python.org), you check the box that says **"Add Python to PATH"**. Tkinter is usually included by default.
    -   Install a MySQL server using a tool like [XAMPP](https://www.apachefriends.org/index.html) or the official [MySQL Community Server](https://dev.mysql.com/downloads/mysql/) installer.

2.  **Setup Python Environment:**

    Create a file named `requirements.txt` in the root of the project directory with the following content:
    ```
    customtkinter
    mysql-connector-python
    PyMuPDF
    Faker
    ```
    Then, install the libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database Seeding:**

    This is a **mandatory** step before running the main application for the first time. This script will set up the database schema, populate it with data from the `/data` directory, and encrypt the applicant profiles.

    Run the script from the project's root directory:
    ```bash
    # On Linux/macOS
    python3 src/load_data.py

    # On Windows
    python src/load_data.py
    ```
    You will be prompted to enter your MySQL password. After the first successful run, it will create a `config.ini` file to store your credentials securely, so you won't need to enter them again.

## Running the Application

After completing the installation and setup, you can run the main application.

```bash
# On Linux/macOS
python3 src/main.py

# On Windows
python src/main.py
```
The CV Analyzer application window will appear and will be ready for use.

## Authors

This project was developed by the group "paraPencariKerja", consisting of:

-   **12821046** - Fardhan Indrayesa
-   **13523041** - Hanif Kalyana Aditya
-   **13523072** - Sabilul Huda
