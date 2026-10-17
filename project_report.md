# Project Report
## Web-Based Student Academic Requisition Form with PDF Generation

### 1. Objective
To develop a Python web application that allows students to enter requisition details online, confirm the student declaration, and download a completed PDF based on the institute's Student Academic Requisition Form.

### 2. Technologies Used
- Python
- Streamlit for the web interface
- ReportLab for PDF generation
- SQLite for local data storage

### 3. Main Modules
1. Student input form
2. Input validation
3. Student declaration confirmation
4. PDF generation and download
5. SQLite record storage
6. Basic search by roll number

### 4. Validation
The app checks mandatory fields, validates email or a 10-digit mobile number, requires document names when the student selects Yes for supporting documents, and blocks generation until the declaration checkbox is accepted.

### 5. PDF Format
The generated PDF follows the supplied form's section sequence: student details, purpose, supporting documents, student declaration, HoD processing, forwarding/signature/remarks, and Principal Office use. HoD and Principal decision/signature/remarks fields are intentionally left blank.

### 6. Data Storage
Each valid submission is stored in a local SQLite database with an automatically generated requisition number. The database file is created when the app first runs.

### 7. Limitations and Future Scope
The current version does not upload supporting documents or student signatures. The PDF is a close recreation rather than an exact overlay of the original Word template. Future improvements include using the institute's exact template as a fillable background, authentication for an admin dashboard, status tracking, and secure hosted database storage.

### 8. How to Run
Install packages from `requirements.txt` and run `streamlit run app.py`.
