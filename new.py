import streamlit as st
from streamlit_image_select import image_select
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
from transformers import pipeline
import torch
from PIL import Image
from textwrap import wrap
import base64,os
import streamlit.components.v1 as components
from pdf2image import convert_from_bytes

@st.cache_resource
def load_template_images():
    imgs = []
    for i in range(8):
        path = os.path.join("templates", f"C:\\workplace\\resume_builder\\.venv\\Lib\\site-packages\\streamlit_image_select\\frontend\\build\\template\\template{i+1}.png")
        if os.path.exists(path):
            with open(path, "rb") as f:
                imgs.append(base64.b64encode(f.read()).decode())
        else:
            imgs.append(None)
    return imgs

template_names = [f"Template{i}" for i in range(1, 9)]
template_images = load_template_images()

defaults = {
    'name': '', 'email': '', 'phone': '',
    'summary': '', 'education': '', 'experience': '',
    'skills': '', 'languages': '', 'certificates': '',
    'awards': '', 'interests': '',
    'selected_template': 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

@st.cache_resource(show_spinner="Loading AI model...")
def load_paraphraser():
    try:
        return pipeline("text2text-generation", model="google/flan-t5-base", device="cpu")
    except Exception as e:
        st.error(f"AI model failed to load: {e}")
        return None

paraphraser = load_paraphraser()

@st.cache_data(ttl=3600)
def enhance_section(section, value):
    if paraphraser is None:
        return value
    try:
        prompt = f"Correct grammar and rewrite this {section} to sound professional, polished, and concise:\n{value.strip()}"
        out = paraphraser(prompt, max_length=128, num_return_sequences=1)
        return out[0]["generated_text"] if out else value
    except Exception as e:
        st.warning(f"Enhancement failed for {section}: {e}")
        return value

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://i.pinimg.com/736x/e4/fa/f9/e4faf95052527c2025e70bf13c506f6a.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        height: 100vh;
        width: 100vw;
    }
    .main, .block-container {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def wrap_text(text, width):
    lines = []
    for line in text.split('\n'):
        lines.extend(wrap(line.strip(), width))
    return lines

def template_template1(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    # Your existing template_template1 code here, unchanged
    width, height = A4
    margin_bottom = 50
    sidebar_x = 0
    sidebar_width = width * 0.3
    content_x = sidebar_width + 10

    first_page = True
    y = height - 60
    page_number = 1

    def draw_sidebar():
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.rect(sidebar_x, 0, sidebar_width, height, fill=1)

        if profile_photo_bytes:
            image_io = io.BytesIO(profile_photo_bytes)
            img = ImageReader(image_io)
            c.drawImage(img, 40, height - 120, width=80, height=80, mask='auto')

        sidebar_y = height - 140
        def draw_sidebar_section(title, content):
            nonlocal sidebar_y
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.white)
            c.drawString(40, sidebar_y, f"• {title}")
            sidebar_y -= 18
            c.setFont("Helvetica", 10)
            for line in wrap_text(content, 32):
                c.drawString(50, sidebar_y, f"- {line}")
                sidebar_y -= 14
            sidebar_y -= 10

        draw_sidebar_section("SKILLS", skills)
        draw_sidebar_section("LANGUAGES", languages)
        draw_sidebar_section("CERTIFICATES", certificates)
        draw_sidebar_section("HONOR AWARDS", awards)
        draw_sidebar_section("INTERESTS", interests)

    def draw_left_bar_background():
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.rect(sidebar_x, 0, sidebar_width, height, fill=1)

    def draw_header():
        nonlocal y
        y = height - 60
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.drawString(content_x, y, name)
        y -= 20
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor("#7F8C8D"))
        c.drawString(content_x, y, f"Email: {email} | Phone: {phone}")
        y -= 30

    def draw_footer(page_num):
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#7F8C8D"))
        footer_text = f"Page {page_num}"
        text_width = c.stringWidth(footer_text, "Helvetica", 9)
        c.drawString((width - text_width) / 2, 20, footer_text)

    def check_page_break(extra_space_needed=60):
        nonlocal y, first_page, page_number
        if y < margin_bottom + extra_space_needed:
            draw_footer(page_number)
            c.showPage()
            page_number += 1
            if first_page:
                first_page = False
            draw_left_bar_background()
            draw_header()

    def draw_main_block(title, content):
        nonlocal y
        check_page_break()
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.drawString(content_x, y, f"• {title}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        for line in wrap_text(content, 75):
            check_page_break()
            c.drawString(content_x + 10, y, line)
            y -= 12
        y -= 10

    def draw_main_section(title, content):
        nonlocal y
        check_page_break()
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#2C3E50"))
        c.drawString(content_x, y, f"• {title}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        for line in content.split('\n'):
            check_page_break()
            if '|' in line:
                parts = line.split('|')
                job_title = parts[0].strip()
                company = parts[1].strip()
                location = parts[2].strip() if len(parts) > 2 else ''
                duration = parts[3].strip() if len(parts) > 3 else ''
                c.setFont("Helvetica-Bold", 10)
                c.drawString(content_x + 10, y, job_title)
                y -= 12
                c.setFont("Helvetica", 9)
                for wrapped_line in wrap(f"{company}, {location} ({duration})", 75):
                    check_page_break()
                    c.drawString(content_x + 12, y, wrapped_line)
                    y -= 12
            else:
                for wrapped_line in wrap(line.strip(), 75):
                    check_page_break()
                    c.drawString(content_x + 10, y, f"- {wrapped_line}")
                    y -= 12
        y -= 10

    y = height - 60
    draw_sidebar()
    draw_header()
    draw_main_block("PROFILE SUMMARY", summary)
    draw_main_section("WORK EXPERIENCE", experience)
    draw_main_section("EDUCATION", education)
    draw_footer(page_number)

def template_template2(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    margin_bottom = 50
    content_x = 55
    y = height - 50
    page_number = 1

    # Draw header
    c.setFillColor(colors.orange)
    c.rect(0, height - 80, width, 80, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(65, height - 50, name)
    c.setFont("Helvetica", 12)
    c.drawString(65, height - 70, f"Email: {email} | Phone: {phone}")

    # Draw profile photo if exists
    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, width - 130, height - 75, width=60, height=60, mask='auto')

    y = height - 100

    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.orange)
    c.drawString(content_x, y, "Profile Summary")
    y -= 14
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for line in wrap_text(summary, 90):
        c.drawString(content_x + 10, y, line)
        y -= 12
    y -= 10

    # Skills
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.orange)
    c.drawString(content_x, y, "Skills")
    y -= 15
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for s in skills.split('\n'):
        c.drawString(content_x + 10, y, f"- {s}")
        y -= 12
    y -= 8

    # Experience as a visual table
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.orange)
    c.drawString(content_x, y, "Experience")
    y -= 16
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for exp in experience.split('\n'):
        row = [part.strip() for part in exp.split('|')]
        try:
            job, company, duration = row[:3]
            c.drawString(content_x + 10, y, f"{job} ({duration})")
            y -= 12
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(content_x + 18, y, company)
            c.setFont("Helvetica", 10)
            y -= 10
        except:
            c.drawString(content_x + 10, y, exp)
            y -= 12
    y -= 8

    # Education
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.orange)
    c.drawString(content_x, y, "Education")
    y -= 15
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for line in education.split('\n'):
        c.drawString(content_x + 10, y, line)
        y -= 12
    y -= 8

    # Certificates, Awards, Interests
    for section, data in [("Certificates", certificates), ("Awards", awards), ("Interests", interests), ("Languages", languages)]:
        if data.strip():
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.orange)
            c.drawString(content_x, y, section)
            y -= 14
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for val in data.split('\n'):
                c.drawString(content_x + 10, y, f"- {val}")
                y -= 12
            y -= 8
    y = height - 60

def template_template3(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    y = height - 60
    margin_left = 45
    section_gap = 16

    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, width - 130, height - 75, width=60, height=60, mask='auto')

    # Name (centered)
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.black)
    c.drawCentredString(width // 2, y, name)
    y -= 24

    # Contact line
    c.setFont("Helvetica", 10)
    c.drawCentredString(width // 2, y, f"{email} | {phone}")
    y -= 14

    # Line separator
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(35, y, width-35, y)
    y -= 18

    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y, "Profile Summary")
    y -= 13
    c.setFont("Helvetica", 10)
    for line in wrap_text(summary, 90):
        c.drawString(margin_left + 8, y, line)
        y -= 11
    y -= section_gap

    # Experience
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_left, y, "Experience")
    y -= 13
    c.setFont("Helvetica", 10)
    for exp in experience.split('\n'):
        c.drawString(margin_left + 8, y, f"- {exp}")
        y -= 11
    y -= section_gap

    # Education, skills, languages one after another
    for title, field in [('Education', education), ('Skills', skills), ('Languages', languages)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin_left, y, title)
            y -= 12
            c.setFont("Helvetica", 10)
            for thing in field.split('\n'):
                c.drawString(margin_left + 8, y, f"- {thing}")
                y -= 11
            y -= 8

    # Certificates, Awards, Interests
    for title, field in [('Certificates', certificates), ('Awards', awards), ('Interests', interests)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin_left, y, title)
            y -= 12
            c.setFont("Helvetica", 10)
            for thing in field.split('\n'):
                c.drawString(margin_left + 8, y, f"- {thing}")
                y -= 11
            y -= 8

def template_template4(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    sidebar_width = width * 0.32
    content_x = sidebar_width + 20
    y = height - 60

    # Sidebar - gray
    c.setFillColor(colors.lightgrey)
    c.rect(0, 0, sidebar_width, height, fill=1)

    # Profile photo
    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, 38, height - 135, width=90, height=90, mask='auto')

    # Sidebar sections (Skills, Languages, Interests)
    sb_y = height - 150
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    for title, field in [("Skills", skills), ("Languages", languages), ("Interests", interests)]:
        if field.strip():
            c.drawString(38, sb_y, title)
            sb_y -= 14
            c.setFont("Helvetica", 9)
            for val in field.split('\n'):
                c.drawString(46, sb_y, f"- {val}")
                sb_y -= 12
            sb_y -= 8
            c.setFont("Helvetica-Bold", 10)

    # Main
    c.setFont("Helvetica-Bold", 19)
    c.setFillColor(colors.black)
    c.drawString(content_x, y, name)
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(content_x, y, f"{email} | {phone}")
    y -= 13

    c.setFont("Helvetica-Bold", 12)
    c.drawString(content_x, y, "Summary")
    y -= 13
    c.setFont("Helvetica", 10)
    for line in wrap_text(summary, 80):
        c.drawString(content_x + 8, y, line)
        y -= 11
    y -= 8

    for title, field in [("Experience", experience), ("Education", education), ("Certificates", certificates), ("Awards", awards)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(content_x, y, title)
            y -= 13
            c.setFont("Helvetica", 10)
            for val in field.split('\n'):
                c.drawString(content_x + 8, y, f"- {val}")
                y -= 11
            y -= 8

def template_template5(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    y = height - 42

    # Thin blue top bar
    c.setFillColor(colors.blue)
    c.rect(0, height-40, width, 40, fill=1)

    # Name/contact
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.white)
    c.drawString(42, height-23, name)
    c.setFont("Helvetica", 10)
    c.drawString(42, height-39, f"{email} | {phone}")
    y = height - 55

    # Photo
    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, width - 100, height - 80, width=50, height=50, mask='auto')

    # Education first
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.blue)
    c.drawString(42, y, "Education")
    y -= 14
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for line in education.split('\n'):
        c.drawString(52, y, f"- {line}")
        y -= 12
    y -= 7

    # Then summary, then the rest
    for title, field in [("Summary", summary), ("Experience", experience), ("Skills", skills), ("Languages", languages), ("Certificates", certificates), ("Awards", awards), ("Interests", interests)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.blue)
            c.drawString(42, y, title)
            y -= 13
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for val in field.split('\n'):
                c.drawString(52, y, f"- {val}")
                y -= 11
            y -= 7

def template_template6(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    sidebar_width = 90
    content_x = sidebar_width + 34
    y = height - 56

    # Sidebar background
    c.setFillColor(colors.HexColor("#1B263B"))
    c.rect(0, 0, sidebar_width, height, fill=1)
    sb_y = height - 65

    # Profile photo (large, circular crop suggested for best look)
    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, 18, height - 95, width=60, height=60, mask='auto')
        sb_y -= 72

    # Sidebar sections (Skills, Languages, Interests, Certificates)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.white)
    for title, field in [("SKILLS", skills), ("LANGUAGES", languages), ("INTERESTS", interests), ("CERTIFICATES", certificates)]:
        if field.strip():
            c.drawString(18, sb_y, title)
            sb_y -= 12
            c.setFont("Helvetica", 9)
            for val in field.split('\n'):
                c.drawString(22, sb_y, f"- {val}")
                sb_y -= 11
            sb_y -= 10
            c.setFont("Helvetica-Bold", 10)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#A9BCD0"))
    c.drawString(18, 24, "professional resume")

    # Main content
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#222831"))
    c.drawString(content_x, y, name)
    y -= 26
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#4F4F4F"))
    c.drawString(content_x, y, f"E: {email}   M: {phone}")
    y -= 20

    c.setStrokeColor(colors.HexColor("#A9BCD0"))
    c.setLineWidth(2)
    c.line(content_x, y, width-36, y)
    y -= 18

    # Modular sections with professional headers
    for title, field in [("SUMMARY", summary), ("EXPERIENCE", experience), ("EDUCATION", education), ("AWARDS", awards)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.HexColor("#1B263B"))
            c.drawString(content_x, y, title)
            y -= 14
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for val in field.split('\n'):
                c.drawString(content_x + 8, y, f"- {val}")
                y -= 11
            y -= 11

def template_template7(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    y = height - 55

    # Photo in box left
    if profile_photo_bytes:
        c.setFillColor(colors.cyan)
        c.rect(42, y-10, 54, 54, fill=1)
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, 45, y-7, width=48, height=48, mask='auto')

    # Name, contact right of photo
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#008080"))
    c.drawString(110, y+32, name)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(110, y+17, f"{email} | {phone}")

    # Skills block right of contact
    c.setFillColor(colors.lightgrey)
    c.rect(110, y, 300, 17, fill=1)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#008080"))
    c.drawString(116, y+3, "Skills: " + ", ".join(skills.split('\n')))
    y -= 27

    # Main vertical sections
    for title, field in [("Summary", summary), ("Experience", experience), ("Education", education), ("Languages", languages), ("Certificates", certificates), ("Awards", awards), ("Interests", interests)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor("#008080"))
            c.drawString(110, y, title)
            y -= 13
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for val in field.split('\n'):
                c.drawString(120, y, f"- {val}")
                y -= 11
            y -= 7


def template_template8(c, name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests, profile_photo_bytes):
    width, height = A4
    sidebar_width = 98
    content_x = sidebar_width + 38
    y = height - 60

    # Sidebar
    c.setFillColor(colors.HexColor("#232b32"))
    c.rect(0, 0, sidebar_width, height, fill=1)
    sb_y = height - 70
    if profile_photo_bytes:
        img = ImageReader(io.BytesIO(profile_photo_bytes))
        c.drawImage(img, 22, height - 108, width=64, height=64, mask='auto')
        sb_y -= 76
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.white)
    for section, field in [("Skills", skills), ("Languages", languages), ("Certificates", certificates), ("Interests", interests)]:
        if field.strip():
            c.drawString(18, sb_y, section)
            sb_y -= 13
            c.setFont("Helvetica", 9)
            for val in field.split('\n'):
                c.drawString(26, sb_y, val)
                sb_y -= 11
            sb_y -= 10
            c.setFont("Helvetica-Bold", 11)

    # Main Content
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#232b32"))
    c.drawString(content_x, y, name)
    y -= 26
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#636e72"))
    c.drawString(content_x, y, f"E: {email}   M: {phone}")
    y -= 20

    c.setStrokeColor(colors.HexColor("#232b32"))
    c.setLineWidth(2)
    c.line(content_x, y, width-36, y)
    y -= 18

    for section, field in [("Summary", summary), ("Experience", experience), ("Education", education), ("Awards", awards)]:
        if field.strip():
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.HexColor("#232b32"))
            c.drawString(content_x, y, section)
            y -= 14
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            for val in field.split('\n'):
                c.drawString(content_x + 8, y, val)
                y -= 11
            y -= 13

def generate_pdf_resume(name,email,phone,summary,education,skills,experience,languages,certificates,awards,interests,profile_photo_bytes,template):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    template = template.lower()  # Ensure lowercase for matching function names
    if template == "template1":
        template_template1(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template2":
        template_template2(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template3":
        template_template3(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template4":
        template_template4(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template5":
        template_template5(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template6":
        template_template6(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template7":
        template_template7(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    elif template == "template8":
        template_template8(c,name, email, phone, summary, education, skills, experience, languages, certificates, awards, interests,profile_photo_bytes)
    else:
        c.drawString(100, 800, f"Resume for {name}")
        c.drawString(100, 780, f"Template '{template}' not found. Using basic layout.")
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Resume Builder")
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Personal Info","Summary","Academics","Professional Info","Achievements","Interests","Choose Template","Submission"])

with tab1:
    uploaded_photo = st.file_uploader("Upload profile photo", type=["jpg", "png", "jpeg"])
    profile_photo_bytes = None
    if uploaded_photo is not None:
        profile_photo_bytes = uploaded_photo.getvalue()
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

with tab2:
    def update_summary():
        st.session_state['summary'] = st.session_state['summary_input']

    summary_input = st.text_area("Summary", value=st.session_state.get("summary", ""),height=150,key='summary_input', on_change=update_summary)

with tab3:
    def update_education():
        st.session_state['education'] = st.session_state['education_input']

    def update_languages():
        st.session_state['languages'] = st.session_state['languages_input']

    education_input = st.text_area("Education", value=st.session_state.get("education", ""),height=100,key='education_input', on_change=update_education)
    languages_input = st.text_area("Languages",  value=st.session_state.get("languages", ""), height=75,key='languages_input', on_change=update_languages)

with tab4:
    def update_experience():
        st.session_state['experience'] = st.session_state['experience_input']
    def update_skills():
            st.session_state['skills'] = st.session_state['skills_input']
    experience_input = st.text_area("Experience", value=st.session_state.get("experience", ""), height=150,key='experience_input', on_change=update_experience)
    skills_input = st.text_area("Skills", value=st.session_state.get("skills", ""),height=100,key='skills_input', on_change=update_skills)

with tab5:
    def update_certificates():
            st.session_state['certificates'] = st.session_state['certificates_input']
    def update_awards():
            st.session_state['awards'] = st.session_state['awards_input']
    certificates_input = st.text_area("Certificates", value=st.session_state.get("certificates", ""),height=75,key='certificates_input', on_change=update_certificates)
    awards_input = st.text_area("Awards", value=st.session_state.get("awards", ""),height=75,key='awards_input', on_change=update_summary)

with tab6:
    def update_interests():
            st.session_state['interests'] = st.session_state['interests_input']
    interests_input = st.text_area("Interests", value=st.session_state.get("interests", ""),height=75,key='interests_input', on_change=update_interests)

with tab7:
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = 0

    st.markdown("### Choose template")

    cols = st.columns(4)
    for i, (name, img_b64) in enumerate(zip(template_names, template_images)):
        col = cols[i % 4]
        # Show preview (even if image missing)
        if img_b64:
            col.image(f"data:image/png;base64,{img_b64}", width="stretch")
        else:
            col.info(f"No preview for {name}")

        # Select button toggles the index in session state
        if col.button(f"Select {name}", key=f"template_btn_{i}"):
            st.session_state['selected_template'] = i

        # Indicate selection
        if st.session_state['selected_template'] == i:
            col.markdown(f"Selected: {name}")

    sel_idx = st.session_state['selected_template']
    st.markdown(f"#### Selected: {template_names[sel_idx]}")
    if template_images[sel_idx]:
        st.image(f"data:image/png;base64,{template_images[sel_idx]}", width="stretch")

with tab8:
    st.markdown("### Enhance and Export")

    # Always render the Enhance button
    if st.button("Enhance Resume with AI"):
        with st.spinner("Enhancing..."):
            fields = ['name', 'summary', 'education', 'experience', 'skills', 'languages', 'certificates', 'awards',
                      'interests']
            for f in fields:
                val = st.session_state.get(f, '')
                if val.strip():
                    st.session_state[f] = enhance_section(f, val)
        st.success("Enhanced. Preview below.")

    # Build current values
    name = st.session_state['name']
    email = st.session_state['email']
    phone = st.session_state['phone']
    summary = st.session_state['summary']
    education = st.session_state['education']
    experience = st.session_state['experience']
    skills = st.session_state['skills']
    languages = st.session_state['languages']
    certificates = st.session_state['certificates']
    awards = st.session_state['awards']
    interests = st.session_state['interests']
    sel_idx = st.session_state['selected_template']
    selectedtemplate = template_names[sel_idx].lower()

    # Always try to generate preview PDF; if required fields missing, show message but keep buttons visible
    buf = None
    try:
        buf = generate_pdf_resume(
            name, email, phone, summary, education, skills, experience,
            languages, certificates, awards, interests, profile_photo_bytes, selectedtemplate
        )
        pdf_bytes = buf.getvalue()
        pages = convert_from_bytes(pdf_bytes, first_page=0, last_page=1)
        st.image(pages[0], caption="PDF Preview",width="stretch")
    except Exception as e:
        st.warning(f"Preview unavailable: {e}")

    # Always render the Download button; validate on click
    if st.button("Generate PDF"):
        if not (name and email and phone):
            st.error("Name, Email, and Phone are required to generate the PDF.")
        else:
            if buf is None:
                # regenerate buffer if needed
                buf = generate_pdf_resume(
                    name, email, phone, summary, education, skills, experience,
                    languages, certificates, awards, interests, profile_photo_bytes, selectedtemplate
                )
            st.success("PDF ready. Click to download.")
            st.download_button(
                "Download PDF Resume",
                data=buf.getvalue(),
                file_name=f"{name}_resume.pdf",
                mime="application/pdf"
            )