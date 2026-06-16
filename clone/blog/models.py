# models.py
# ─────────────────────────────────────────────────────
# This file defines the Blog TABLE in the database
# Each class = one table
# Each Mapped field = one column in that table
# ─────────────────────────────────────────────────────

from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Blog(Base):
    __tablename__ = "blogs"   # this is the actual table name in blog.db

    # Mapped[int] means this column stores an integer
    # primary_key=True means this is the unique ID (auto increments: 1, 2, 3...)
    id: Mapped[int] = mapped_column(primary_key=True)

    # Mapped[str] means this column stores text
    # String(100) means max 100 characters allowed
    title:    Mapped[str] = mapped_column(String(100))
    author:   Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))

    # Text means unlimited length text (used for long blog content)
    content: Mapped[str] = mapped_column(Text)

    # Optional[str] means this column can be empty (nullable)
    # We store multiple image filenames as: "img1.jpg,img2.jpg,img3.jpg"
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # This is a helper method (not a column)
    # It splits the comma string into a proper Python list
    # Example: "img1.jpg,img2.jpg" → ["img1.jpg", "img2.jpg"]
    def image_list(self):
        if self.images:
            return self.images.split(",")
        return []   # return empty list if no images
