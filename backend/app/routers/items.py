from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import models, schemas

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[schemas.Item])
def get_items(
    subcategory_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all items, optionally filtered by subcategory."""
    query = db.query(models.Item)
    if subcategory_id:
        query = query.filter(models.Item.subcategory_id == subcategory_id)
    items = query.all()
    return items


@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID."""
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    # Verify subcategory exists
    subcategory = db.query(models.Subcategory).filter(
        models.Subcategory.id == item.subcategory_id
    ).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    # Create item
    item_data = item.model_dump(exclude={"keywords"})
    db_item = models.Item(**item_data)
    db.add(db_item)
    db.flush()

    # Add keywords
    if item.keywords:
        for keyword in item.keywords:
            db_keyword = models.ItemKeyword(
                item_id=db_item.id,
                keyword=keyword.lower().strip()
            )
            db.add(db_keyword)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update an item."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item.model_dump(exclude_unset=True, exclude={"keywords"})
    for field, value in update_data.items():
        setattr(db_item, field, value)

    # Update keywords if provided
    if item.keywords is not None:
        # Delete existing keywords
        db.query(models.ItemKeyword).filter(
            models.ItemKeyword.item_id == item_id
        ).delete()

        # Add new keywords
        for keyword in item.keywords:
            db_keyword = models.ItemKeyword(
                item_id=item_id,
                keyword=keyword.lower().strip()
            )
            db.add(db_keyword)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}
