# main.py — Blog App Routes (CRUD)

import os
import uuid
from typing import List
from fastapi import FastAPI, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import engine, get_db, Base
from models import Blog

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog App")
templates = Jinja2Templates(directory="frontend")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

UPLOAD_DIR = "uploads"

# Save uploaded images to disk, returns "img1.jpg,img2.jpg"
def save_images(files: List[UploadFile]) -> str | None:
    saved = []
    for file in files:
        if not file or not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        # only allow image file types
        if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            raise HTTPException(status_code=400, detail=f"File type '{ext}' is not allowed. Use jpg, png, gif or webp.")
        filename = f"{uuid.uuid4().hex}{ext}"
        try:
            with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
                f.write(file.file.read())
            saved.append(filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    return ",".join(saved) if saved else None


# ── READ ALL ──
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    try:
        blogs = db.scalars(select(Blog)).all()
        return templates.TemplateResponse(request=request, name="index.html", context={"blogs": blogs})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load blogs: {str(e)}")


# ── CREATE ──
@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse(request=request, name="create.html")

@app.post("/create")
def create_blog(
    title:    str = Form(...),
    author:   str = Form(...),
    category: str = Form(...),
    content:  str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        images_str = save_images(images) if images else None
        db.add(Blog(title=title, author=author, category=category, content=content, images=images_str))
        db.commit()
        return RedirectResponse(url="/", status_code=303)
    except HTTPException:
        raise   # re-raise our own HTTP exceptions (e.g. bad file type)
    except Exception as e:
        db.rollback()  # undo any partial changes
        raise HTTPException(status_code=500, detail=f"Could not create blog: {str(e)}")


# ── READ ONE ──
@app.get("/blog/{blog_id}", response_class=HTMLResponse)
def view_blog(request: Request, blog_id: int, db: Session = Depends(get_db)):
    blog = db.get(Blog, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")
    return templates.TemplateResponse(request=request, name="view.html", context={"blog": blog})


# ── UPDATE ──
@app.get("/update/{blog_id}", response_class=HTMLResponse)
def update_page(request: Request, blog_id: int, db: Session = Depends(get_db)):
    blog = db.get(Blog, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")
    return templates.TemplateResponse(request=request, name="update.html", context={"blog": blog})

@app.post("/update/{blog_id}")
def update_blog(
    blog_id:  int,
    title:    str = Form(...),
    author:   str = Form(...),
    category: str = Form(...),
    content:  str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    blog = db.get(Blog, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")
    try:
        blog.title    = title
        blog.author   = author
        blog.category = category
        blog.content  = content
        new_images = save_images(images) if images else None
        if new_images:
            existing = blog.images or ""
            blog.images = ",".join(filter(None, [existing, new_images]))
        db.commit()
        return RedirectResponse(url=f"/blog/{blog_id}", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not update blog: {str(e)}")


# ── DELETE ──
@app.get("/delete/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.get(Blog, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {blog_id} not found")
    try:
        db.delete(blog)
        db.commit()
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not delete blog: {str(e)}")
