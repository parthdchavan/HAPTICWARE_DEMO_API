from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

# ─────────────────────────────────────────
# STEP 1: CONNECT TO DATABASE
# Think of this like opening a connection to your Excel file (but it's a database)
# ─────────────────────────────────────────
engine = create_engine("sqlite:///students.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# ─────────────────────────────────────────
# STEP 2: DEFINE THE TABLE (like columns in Excel)
# Each field = one column in the "students" table
# ─────────────────────────────────────────
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)        # auto ID: 1, 2, 3...
    name: Mapped[str] = mapped_column(String(50))             # full name
    roll_no: Mapped[str] = mapped_column(String(20), unique=True)  # unique roll number
    email: Mapped[str] = mapped_column(String(100), unique=True)   # unique email
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)   # optional
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # optional
    year: Mapped[Optional[int]] = mapped_column(nullable=True)    # optional year (1/2/3/4)

# This creates the table in the database if it doesn't exist
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────
# STEP 3: DEFINE DATA SHAPES (what user sends & what API returns)
# Pydantic validates the data automatically
# ─────────────────────────────────────────

# What the user sends when creating/updating a student
class StudentIn(BaseModel):
    name: str
    roll_no: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = None

# What the API sends back (includes the auto-generated id)
class StudentOut(StudentIn):
    id: int

    class Config:
        from_attributes = True  # allows reading SQLAlchemy objects

# ─────────────────────────────────────────
# STEP 4: CREATE THE APP
# ─────────────────────────────────────────
app = FastAPI(title="Student API", version="1.0.0")

# Allow frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Opens DB session for each request, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────
# STEP 5: API ROUTES (the actual endpoints)
# ─────────────────────────────────────────

# Home route - just a welcome message
@app.get("/")
def home():
    return {"message": "Student API is running!", "docs": "http://127.0.0.1:8000/docs"}

# CREATE - Add a new student
@app.post("/students/", response_model=StudentOut)
def create_student(data: StudentIn, db: Session = Depends(get_db)):
    if db.scalars(select(Student).where(Student.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.scalars(select(Student).where(Student.roll_no == data.roll_no)).first():
        raise HTTPException(status_code=400, detail="Roll number already exists")
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

# READ ALL - Get list of all students
@app.get("/students/", response_model=list[StudentOut])
def get_all_students(db: Session = Depends(get_db)):
    return db.scalars(select(Student)).all()

# READ ONE - Get a single student by ID
@app.get("/students/{id}", response_model=StudentOut)
def get_student(id: int, db: Session = Depends(get_db)):
    student = db.get(Student, id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# UPDATE - Edit an existing student's info
@app.put("/students/{id}", response_model=StudentOut)
def update_student(id: int, data: StudentIn, db: Session = Depends(get_db)):
    student = db.get(Student, id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in data.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

# DELETE - Remove a student by ID
@app.delete("/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    student = db.get(Student, id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": f"Student {id} deleted successfully"}
