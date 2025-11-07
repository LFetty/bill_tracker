from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models, schemas

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories with their subcategories."""
    categories = db.query(models.Category).all()
    return categories


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    # Check if category name already exists
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}


# Subcategory endpoints
@router.post("/subcategories", response_model=schemas.Subcategory)
def create_subcategory(subcategory: schemas.SubcategoryCreate, db: Session = Depends(get_db)):
    """Create a new subcategory."""
    # Verify category exists
    category = db.query(models.Category).filter(models.Category.id == subcategory.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Create subcategory
    subcategory_data = subcategory.model_dump(exclude={"keywords"})
    db_subcategory = models.Subcategory(**subcategory_data)
    db.add(db_subcategory)
    db.flush()

    # Add keywords
    if subcategory.keywords:
        for keyword in subcategory.keywords:
            db_keyword = models.CategoryKeyword(
                subcategory_id=db_subcategory.id,
                keyword=keyword
            )
            db.add(db_keyword)

    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory


@router.get("/subcategories/{subcategory_id}", response_model=schemas.Subcategory)
def get_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    """Get a specific subcategory by ID."""
    subcategory = db.query(models.Subcategory).filter(models.Subcategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory


@router.put("/subcategories/{subcategory_id}", response_model=schemas.Subcategory)
def update_subcategory(subcategory_id: int, subcategory: schemas.SubcategoryUpdate, db: Session = Depends(get_db)):
    """Update a subcategory."""
    db_subcategory = db.query(models.Subcategory).filter(models.Subcategory.id == subcategory_id).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    update_data = subcategory.model_dump(exclude_unset=True, exclude={"keywords"})
    for field, value in update_data.items():
        setattr(db_subcategory, field, value)

    # Update keywords if provided
    if subcategory.keywords is not None:
        # Delete existing keywords
        db.query(models.CategoryKeyword).filter(
            models.CategoryKeyword.subcategory_id == subcategory_id
        ).delete()

        # Add new keywords
        for keyword in subcategory.keywords:
            db_keyword = models.CategoryKeyword(
                subcategory_id=subcategory_id,
                keyword=keyword
            )
            db.add(db_keyword)

    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory


@router.delete("/subcategories/{subcategory_id}")
def delete_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    """Delete a subcategory."""
    db_subcategory = db.query(models.Subcategory).filter(models.Subcategory.id == subcategory_id).first()
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    db.delete(db_subcategory)
    db.commit()
    return {"message": "Subcategory deleted successfully"}
