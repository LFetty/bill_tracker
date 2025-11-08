from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Category Schemas
class CategoryKeywordBase(BaseModel):
    keyword: str


class CategoryKeywordCreate(CategoryKeywordBase):
    pass


class CategoryKeyword(CategoryKeywordBase):
    id: int
    subcategory_id: int

    class Config:
        from_attributes = True


class SubcategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class SubcategoryCreate(SubcategoryBase):
    category_id: int
    keywords: Optional[List[str]] = []


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class Subcategory(SubcategoryBase):
    id: int
    category_id: int
    created_at: datetime
    keywords: List[CategoryKeyword] = []
    items: List['Item'] = []

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    subcategories: List[Subcategory] = []

    class Config:
        from_attributes = True


# Item Schemas
class ItemKeywordBase(BaseModel):
    keyword: str


class ItemKeywordCreate(ItemKeywordBase):
    pass


class ItemKeyword(ItemKeywordBase):
    id: int
    item_id: int

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    subcategory_id: int
    keywords: Optional[List[str]] = []


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class Item(ItemBase):
    id: int
    subcategory_id: int
    created_at: datetime
    keywords: List[ItemKeyword] = []

    class Config:
        from_attributes = True


# Bill Item Schemas
class BillItemBase(BaseModel):
    product_name: str
    amount: float
    subcategory_id: Optional[int] = None
    item_id: Optional[int] = None


class BillItemCreate(BillItemBase):
    pass


class BillItemUpdate(BaseModel):
    product_name: Optional[str] = None
    amount: Optional[float] = None
    subcategory_id: Optional[int] = None
    item_id: Optional[int] = None


class BillItem(BillItemBase):
    id: int
    bill_id: int
    created_at: datetime
    subcategory: Optional[Subcategory] = None
    item: Optional[Item] = None

    class Config:
        from_attributes = True


# Bill Schemas
class BillBase(BaseModel):
    date: Optional[datetime] = None
    store_name: Optional[str] = None
    total: Optional[float] = 0.0
    notes: Optional[str] = None


class BillCreate(BillBase):
    items: List[BillItemCreate] = []


class BillUpdate(BaseModel):
    date: Optional[datetime] = None
    store_name: Optional[str] = None
    total: Optional[float] = None
    notes: Optional[str] = None
    items: Optional[List[BillItemCreate]] = None


class Bill(BillBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    items: List[BillItem] = []

    class Config:
        from_attributes = True


# OCR Response Schema
class OCRItem(BaseModel):
    product_name: str
    amount: float
    suggested_subcategory_id: Optional[int] = None
    suggested_item_id: Optional[int] = None


class OCRResponse(BaseModel):
    items: List[OCRItem]
    total: Optional[float] = None
    store_name: Optional[str] = None
    raw_text: str
