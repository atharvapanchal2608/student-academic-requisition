import io
import os
import re
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "requisitions.db"
APPLICATION_TYPES = [
    "Bonafide", "Student Certificate", "Scholarship", "NOC",
    "Academic Permission", "Examination", "Internship", "Placement",
    "Other Request",
]
DECLARATION = (
    "I certify that the information provided above is correct and that the request "
    "is being submitted for academic purposes. I understand that the request will "
    "be processed as per applicable Institute/University rules and within the "
    "stipulated processing time."
)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requisition_no TEXT UNIQUE,
                department TEXT NOT NULL,
                student_name TEXT NOT NULL,
                roll_no TEXT NOT NULL,
                semester TEXT NOT NULL,
                division TEXT NOT NULL,
                contact TEXT NOT NULL,
                application_type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                documents_attached TEXT NOT NULL,
                document_names TEXT,
                request_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def wrap_text(text, max_width, font_name="Helvetica", font_size=9):
    words = str(text or "").split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]

def draw_wrapped(c, text, x, y, max_width, font_size=9, leading=12, font="Helvetica"):
    c.setFont(font, font_size)
    for line in wrap_text(text, max_width, font, font_size):
        c.drawString(x, y, line)
        y -= leading
    return y

def line(c, x1, y1, x2, y2, width=0.7):
    c.setLineWidth(width)
    c.setStrokeColor(colors.black)
    c.line(x1, y1, x2, y2)

def section(c, title, y):
    c.setFont("Helvetica-Bold", 10)
    c.drawString(42, y, title)
    line(c, 42, y-4, 553, y-4, 0.5)
    return y-20

def field(c, label, value, x, y, width, label_width=None, font_size=9):
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x, y, label)
    if label_width is None:
        label_width = stringWidth(label, "Helvetica-Bold", font_size) + 4
    c.setFont("Helvetica", font_size)
    lines = wrap_text(value or "", max(30, width-label_width), "Helvetica", font_size)
    if len(lines) <= 1:
        c.drawString(x+label_width, y, lines[0])
        line(c, x+label_width, y-3, x+width, y-3, 0.4)
        return y
    yy = y
    for t in lines:
        c.drawString(x+label_width, yy, t)
        line(c, x+label_width, yy-3, x+width, yy-3, 0.4)
        yy -= 12
    return yy

def generate_pdf(data):
    buff = io.BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    W, H = A4
    left, right = 42, 553

    # Page 1: follows the supplied institute form's section order and labels.
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, H-43, "STUDENT ACADEMIC REQUISITION FORM")
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H-58, "(Autonomous College Affiliated to University of Mumbai)")
    line(c, left, H-68, right, H-68, 1)

    y = H-88
    field(c, "Name of the Department:", data["department"], left, y, 255, 125)
    field(c, "Department Outward No.:", "", 310, y, 135, 112)
    field(c, "Date:", data["request_date"], 450, y, 103, 30)
    y -= 28

    c.setFont("Helvetica-Bold", 8)
    c.drawString(left, y, "Processing Time:")
    y = draw_wrapped(c,
        "The request will normally be processed within 4 working days after receiving the completed form and all required supporting documents. Students are advised to apply in advance, as incomplete applications may require additional processing time.",
        left+78, y, right-left-78, 8, 10)
    y -= 8

    y = section(c, "1. STUDENT DETAILS", y)
    field(c, "Name of Student:", data["student_name"], left, y, 510, 88); y -= 23
    field(c, "Roll No.:", data["roll_no"], left, y, 175, 48)
    field(c, "Semester:", data["semester"], 225, y, 150, 55)
    field(c, "Division:", data["division"], 390, y, 160, 48); y -= 23
    field(c, "Email / Mobile:", data["contact"], left, y, 510, 80); y -= 25
    c.setFont("Helvetica-Bold", 9); c.drawString(left, y, "Application for –")
    c.setFont("Helvetica", 9)
    app_line = data["application_type"]
    c.drawString(left+92, y, app_line)
    line(c, left+92, y-3, right, y-3, 0.4)
    y -= 25

    y = section(c, "2. PURPOSE / BRIEF DETAILS OF REQUEST", y)
    purpose_lines = wrap_text(data["purpose"], right-left-12, "Helvetica", 9)
    c.setFont("Helvetica", 9)
    for txt in purpose_lines[:5]:
        c.drawString(left+5, y, txt); y -= 13
    # Space for additional handwritten notes, matching the original form's open area.
    y -= max(22, 58 - 13*min(len(purpose_lines), 3))
    line(c, left, y, right, y, 0.4)
    y -= 20

    y = section(c, "3. SUPPORTING DOCUMENTS", y)
    c.setFont("Helvetica-Bold", 9); c.drawString(left, y, "Documents attached:")
    c.setFont("Helvetica", 9)
    c.drawString(left+112, y, "[X] Yes" if data["documents_attached"] == "Yes" else "[ ] Yes")
    c.drawString(left+170, y, "[X] No" if data["documents_attached"] == "No" else "[ ] No")
    y -= 22
    field(c, "Document name(s), if applicable:", data["document_names"], left, y, 510, 155); y -= 27

    y = section(c, "4. STUDENT DECLARATION", y)
    y = draw_wrapped(c, DECLARATION, left, y, right-left, 9, 12)
    y -= 10
    field(c, "Student Signature:", "", left, y, 260, 94)
    field(c, "Date:", data["request_date"], 335, y, 215, 30); y -= 34

    y = section(c, "5. HoD Signature:", y)
    field(c, "HoD Signature:", "", left, y, 250, 80)
    field(c, "Remarks:", "", 310, y, 240, 48); y -= 27
    c.setFont("Helvetica-Bold", 8)
    forwarded = "Forwarded to (VICE PRINCIPAL/ CHIEF ACADEMIC OFFICER/ ACCOUNTS/ SPORTS/ PLACEMENT CELL/ SCHOLARSHIP CELL/ EXAM CELL) (if required)"
    y = draw_wrapped(c, forwarded, left, y, right-left, 8, 10)
    y -= 14
    field(c, "Signature:", "", left, y, 250, 55)
    field(c, "Remarks:", "", 310, y, 240, 48)

    c.showPage()

    # Page 2 mirrors the supplied file's continuation page and keeps Principal fields blank.
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W/2, H-43, "STUDENT ACADEMIC REQUISITION FORM")
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H-58, "(Autonomous College Affiliated to University of Mumbai)")
    line(c, left, H-68, right, H-68, 1)
    y = H-98
    y = section(c, "6. PRINCIPAL OFFICE USE ONLY", y)
    c.setFont("Helvetica-Bold", 9); c.drawString(left, y, "Decision by Principal.:")
    c.setFont("Helvetica", 9)
    c.drawString(left+135, y, "[ ] Approved")
    c.drawString(left+235, y, "[ ] Not Approved")
    c.drawString(left+365, y, "[ ] Clarification Required")
    y -= 30
    field(c, "Remarks (if any):", "", left, y, 510, 88)
    y -= 55
    field(c, "Principal Signature:", "", left, y, 510, 105)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(left, 42, "Official-use fields intentionally left blank for institute processing.")
    c.save()
    buff.seek(0)
    return buff.getvalue()

def save_submission(data):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO requisitions
            (requisition_no, department, student_name, roll_no, semester, division,
             contact, application_type, purpose, documents_attached, document_names, request_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["requisition_no"], data["department"], data["student_name"], data["roll_no"],
            data["semester"], data["division"], data["contact"], data["application_type"],
            data["purpose"], data["documents_attached"], data["document_names"], data["request_date"]
        ))
        return cur.lastrowid

st.set_page_config(page_title="Student Academic Requisition", page_icon="📄", layout="centered")
init_db()
st.title("Student Academic Requisition Form")
st.caption("Fill in your details, confirm the declaration, and generate a PDF based on the institute form.")

with st.form("requisition_form"):
    st.subheader("1. Student Details")
    department = st.text_input("Name of Department *", placeholder="e.g., EXCS")
    student_name = st.text_input("Student Name *")
    col1, col2, col3 = st.columns(3)
    roll_no = col1.text_input("Roll Number *")
    semester = col2.selectbox("Semester *", [str(i) for i in range(1, 9)])
    division = col3.text_input("Division *")
    contact = st.text_input("Email / Mobile Number *", placeholder="Enter email or 10-digit mobile number")
    application_type = st.selectbox("Application Type *", APPLICATION_TYPES)

    st.subheader("2. Purpose / Brief Details of Request")
    purpose = st.text_area("Purpose *", placeholder="Briefly explain why you need this requisition.", height=100)

    st.subheader("3. Supporting Documents")
    documents_attached = st.radio("Are supporting documents attached?", ["No", "Yes"], horizontal=True)
    document_names = st.text_input("Name of supporting document(s)", placeholder="e.g., offer letter, scholarship notice")

    st.subheader("4. Student Declaration")
    st.info(DECLARATION)
    declaration_accepted = st.checkbox("I have read and accept the student declaration above. *")
    request_date = st.date_input("Date *", value=date.today()).isoformat()

    submitted = st.form_submit_button("Generate PDF", type="primary", use_container_width=True)

if submitted:
    errors = []
    required = {
        "Name of Department": department,
        "Student Name": student_name,
        "Roll Number": roll_no,
        "Division": division,
        "Email / Mobile Number": contact,
        "Purpose": purpose,
    }
    for label, value in required.items():
        if not value.strip():
            errors.append(f"{label} is required.")
    if "@" in contact:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact.strip()):
            errors.append("Enter a valid email address.")
    elif not re.fullmatch(r"\d{10}", re.sub(r"[\s()+-]", "", contact.strip())):
        errors.append("Enter a valid email address or a 10-digit mobile number.")
    if documents_attached == "Yes" and not document_names.strip():
        errors.append("Enter the supporting document name(s), or change supporting documents to No.")
    if not declaration_accepted:
        errors.append("You must accept the student declaration before generating the PDF.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            count = conn.execute("SELECT COUNT(*) FROM requisitions").fetchone()[0] + 1
        requisition_no = f"SAR-{date.today().strftime('%Y%m%d')}-{count:04d}"
        data = {
            "requisition_no": requisition_no,
            "department": department.strip(),
            "student_name": student_name.strip(),
            "roll_no": roll_no.strip(),
            "semester": semester,
            "division": division.strip(),
            "contact": contact.strip(),
            "application_type": application_type,
            "purpose": purpose.strip(),
            "documents_attached": documents_attached,
            "document_names": document_names.strip(),
            "request_date": request_date,
        }
        try:
            save_submission(data)
            pdf_bytes = generate_pdf(data)
            safe_roll = re.sub(r"[^A-Za-z0-9_-]", "_", data["roll_no"])
            safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", data["student_name"].replace(" ", "_"))
            filename = f"Requisition_{safe_roll}_{safe_name}.pdf"
            st.success(f"PDF generated. Requisition number: {requisition_no}")
            st.download_button("Download PDF", data=pdf_bytes, file_name=filename,
                               mime="application/pdf", use_container_width=True)
        except Exception as exc:
            st.error(f"Could not generate the PDF: {exc}")

with st.expander("Admin / Search (local database)"):
    search_roll = st.text_input("Search by roll number")
    if st.button("Search records"):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT requisition_no, student_name, roll_no, application_type, request_date, created_at
                FROM requisitions WHERE roll_no LIKE ? ORDER BY id DESC LIMIT 100
            """, (f"%{search_roll.strip()}%",)).fetchall()
        if rows:
            st.dataframe([dict(row) for row in rows], use_container_width=True)
        else:
            st.info("No matching records found.")
