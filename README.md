# Web-Based Student Academic Requisition Form with PDF Generation

## Features
- Streamlit online form based on the supplied Student Academic Requisition Form.
- Required-field, email/mobile, and declaration validation.
- PDF generation and download.
- SQLite storage with automatic requisition number.
- Basic local search by roll number.
- Official processing fields remain blank.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment (recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `streamlit run app.py`
6. Open the local URL printed in the terminal.

## Deployment
Push this folder to a GitHub repository, then create a Streamlit Community Cloud app using `app.py` as the entry point and `requirements.txt` for dependencies. The SQLite database is suitable for a classroom demo/local run; ephemeral hosting may reset local database files, so use managed storage for a production deployment.

## Notes
- The PDF recreates the supplied form's section order, wording, and official-use areas in a generated PDF layout. It is a close recreation, not a pixel-perfect fill of the original DOCX.
- The original institute file has a continuation page for the Principal Office section; the generated PDF retains a second page for that section.
- Student signature upload and supporting-file upload are not implemented; supporting document names can be entered.
- This demo stores personal student data in SQLite. Do not deploy publicly with real student information unless access control and data handling are approved by the institute.
