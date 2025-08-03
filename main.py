from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re, os
from datetime import datetime

app = FastAPI()

@app.post("/format-resume/")
async def format_resume(file: UploadFile = File(...)):
    contents = await file.read()
    content = contents.decode("utf-8")

    # Clean and format
    content = re.sub(r"\*Note:.*?deliverables\.\*", "", content, flags=re.DOTALL)
    content = re.sub(r"\*\*(.*?)\*\*", r"\1", content)
    content = re.sub(r"[#•✆✔✓]", "", content)
    content = re.sub(r"\n{3,}", "\n\n", content.strip())
    content = re.sub(r"(?<!\n)\n(?!\n)", " ", content)

    header = (
        "ADITHYA VANKAYALAPATI\n"
        "+1 (940) 977-2236 | vankayalapatiadithya@gmail.com | LinkedIn: http://www.linkedin.com/in/adithya-chowdary02 | Denton, Texas, 76207\n"
    )
    content = re.sub(r"^.*?ADITHYA VANKAYALAPATI.*?Denton, Texas.*?\n", header, content, flags=re.DOTALL)

    section_keywords = [
        "EDUCATION", "PROJECTS", "INTERNSHIPS", "TECHNICAL SKILLS", "SOFT SKILLS",
        "ACHIEVEMENTS", "CERTIFICATIONS", "SUMMARY", "EXPERIENCE", "PUBLICATIONS", 
        "TRAININGS", "CORE COMPETENCIES"
    ]

    char_count = len(content)
    font_size = Pt(10 if char_count > 4000 else 11)

    # Create doc
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = font_size

    def add_paragraph(text, bold=False):
        para = doc.add_paragraph()
        run = para.add_run(text)
        run.bold = bold
        run.font.size = font_size
        para.paragraph_format.line_spacing = Pt(12)
        para.paragraph_format.space_after = Pt(2)
        para.paragraph_format.space_before = Pt(2)
        para.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.upper() in section_keywords or re.match(r"^[A-Z\s]{4,}$", line):
            add_paragraph(line, bold=True)
        else:
            add_paragraph(line)

    filename = f"formatted_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    doc.save(filename)
    return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
