import io
import qrcode
import random
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

from database import (
    init_db, add_student, remove_student,
    get_students, get_attendance, mark_attendance,
    get_student_by_id, get_attendance_stats
)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


current_token = "000000"
token_generated_at = None
TOKEN_EXPIRY_SECONDS = 600


def new_token():
    return str(random.randint(100000, 999999))


def is_token_valid(token, student_token_time=None):
    global current_token, token_generated_at
    
    if token != current_token:
        return False
    
    if token_generated_at is None:
        return False
    
    time_elapsed = (datetime.now() - token_generated_at).total_seconds()
    
    if time_elapsed > TOKEN_EXPIRY_SECONDS:
        return False
    
    return True


def generate_qr(token):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    stats = get_attendance_stats()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats
    })


@app.get("/qr")
def qr_code():
    global current_token, token_generated_at
    current_token = new_token()
    token_generated_at = datetime.now()
    img = generate_qr(current_token)
    return StreamingResponse(img, media_type="image/png", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })


@app.get("/scan", response_class=HTMLResponse)
def scan_page(request: Request):
    return templates.TemplateResponse("scan.html", {"request": request})


@app.post("/scan")
def scan_submit(request: Request, student_id: str = Form(...), token: str = Form(...)):
    student = get_student_by_id(student_id)
    
    if not student:
        return templates.TemplateResponse("scan.html", {
            "request": request,
            "error": f"Student ID '{student_id}' not found. Please check your ID.",
            "student_id": student_id,
            "token": token
        })
    
    if is_token_valid(token):
        success, message = mark_attendance(student_id, "Present")
        return templates.TemplateResponse("scan.html", {
            "request": request,
            "success": f"✓ Welcome {student['name']}! Attendance marked as Present.",
            "student_name": student['name']
        })
    else:
        return templates.TemplateResponse("scan.html", {
            "request": request,
            "error": "Invalid or expired token. Please scan the current QR code.",
            "student_id": student_id
        })


@app.get("/students", response_class=HTMLResponse)
def students_page(request: Request):
    return templates.TemplateResponse("students.html", {
        "request": request,
        "students": get_students()
    })


@app.post("/addstudent")
def add(request: Request, student_id: str = Form(...), name: str = Form(...)):
    success, message = add_student(student_id, name)
    
    students = get_students()
    
    if success:
        return templates.TemplateResponse("students.html", {
            "request": request,
            "students": students,
            "success": message
        })
    else:
        return templates.TemplateResponse("students.html", {
            "request": request,
            "students": students,
            "error": message
        })


@app.post("/removestudent")
def remove(student_id: str = Form(...)):
    remove_student(student_id)
    return RedirectResponse("/students", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    rows = get_attendance()
    stats = get_attendance_stats()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "rows": rows,
        "stats": stats
    })
