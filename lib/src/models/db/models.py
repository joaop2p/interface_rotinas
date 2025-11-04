from sqlmodel import  Relationship, SQLModel, Field
from datetime import datetime
from typing import Optional, List

class Category(SQLModel, table=True):
    __tablename__ = "tb_categories"  # type: ignore

    category_id: int = Field(default=None, primary_key=True)
    category_name: str = Field(unique=True, nullable=False)
    icon: str
    routines: List["Routine"] = Relationship(back_populates="category")

class Routine(SQLModel, table=True):
    __tablename__ = "tb_routines"  # type: ignore

    routine_id: Optional[int] = Field(default=None, primary_key=True)
    routine_name: str
    directory_path: str
    description: Optional[str] = None
    category_id: int = Field(nullable=False, foreign_key="tb_categories.category_id")
    dt_created: datetime = Field(default=datetime.now())
    dt_modified: datetime = Field(default=datetime.now())
    category: "Category" = Relationship(back_populates="routines")