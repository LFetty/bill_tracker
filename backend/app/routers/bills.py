from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import models, schemas

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/", response_model=List[schemas.Bill])
def get_bills(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all bills with optional date filtering."""
    query = db.query(models.Bill)

    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(models.Bill.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(models.Bill.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    bills = query.order_by(models.Bill.date.desc()).offset(skip).limit(limit).all()
    return bills


@router.get("/{bill_id}", response_model=schemas.Bill)
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    """Get a specific bill by ID."""
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.post("/", response_model=schemas.Bill)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    """Create a new bill with items."""
    # Create bill
    bill_data = bill.model_dump(exclude={"items"})
    if bill_data["date"] is None:
        bill_data["date"] = datetime.utcnow()

    db_bill = models.Bill(**bill_data)
    db.add(db_bill)
    db.flush()

    # Add bill items and auto-learn keywords
    total = 0.0
    for item in bill.items:
        db_item = models.BillItem(
            bill_id=db_bill.id,
            **item.model_dump()
        )
        db.add(db_item)
        total += item.amount

        # Auto-learn keywords
        product_keyword = item.product_name.lower().strip()

        # If item has an item_id, add product name as keyword to that item
        if item.item_id and product_keyword:
            existing_item_keyword = db.query(models.ItemKeyword).filter(
                models.ItemKeyword.item_id == item.item_id,
                models.ItemKeyword.keyword == product_keyword
            ).first()

            if not existing_item_keyword:
                new_item_keyword = models.ItemKeyword(
                    item_id=item.item_id,
                    keyword=product_keyword
                )
                db.add(new_item_keyword)

        # Also add to subcategory keywords for backward compatibility
        elif item.subcategory_id and product_keyword:
            existing_keyword = db.query(models.CategoryKeyword).filter(
                models.CategoryKeyword.subcategory_id == item.subcategory_id,
                models.CategoryKeyword.keyword == product_keyword
            ).first()

            if not existing_keyword:
                new_keyword = models.CategoryKeyword(
                    subcategory_id=item.subcategory_id,
                    keyword=product_keyword
                )
                db.add(new_keyword)

    # Update total if not provided
    if bill.total == 0.0:
        db_bill.total = total

    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.put("/{bill_id}", response_model=schemas.Bill)
def update_bill(bill_id: int, bill: schemas.BillUpdate, db: Session = Depends(get_db)):
    """Update a bill."""
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    update_data = bill.model_dump(exclude_unset=True, exclude={"items"})
    for field, value in update_data.items():
        setattr(db_bill, field, value)

    # Update items if provided
    if bill.items is not None:
        # Delete existing items
        db.query(models.BillItem).filter(models.BillItem.bill_id == bill_id).delete()

        # Add new items
        total = 0.0
        for item in bill.items:
            db_item = models.BillItem(
                bill_id=bill_id,
                **item.model_dump()
            )
            db.add(db_item)
            total += item.amount

        # Update total
        db_bill.total = total

    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.delete("/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    """Delete a bill."""
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(db_bill)
    db.commit()
    return {"message": "Bill deleted successfully"}


@router.get("/stats/summary")
def get_spending_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get spending summary by category."""
    query = db.query(models.BillItem)

    # Apply date filters if provided
    if start_date or end_date:
        query = query.join(models.Bill)
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(models.Bill.date >= start)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(models.Bill.date <= end)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

    items = query.all()

    # Group by category and subcategory
    category_totals = {}
    uncategorized_total = 0.0

    for item in items:
        if item.subcategory:
            category_name = item.subcategory.category.name
            subcategory_name = item.subcategory.name

            if category_name not in category_totals:
                category_totals[category_name] = {
                    "total": 0.0,
                    "subcategories": {}
                }

            category_totals[category_name]["total"] += item.amount

            if subcategory_name not in category_totals[category_name]["subcategories"]:
                category_totals[category_name]["subcategories"][subcategory_name] = 0.0

            category_totals[category_name]["subcategories"][subcategory_name] += item.amount
        else:
            uncategorized_total += item.amount

    return {
        "categories": category_totals,
        "uncategorized": uncategorized_total,
        "total": sum(c["total"] for c in category_totals.values()) + uncategorized_total
    }


@router.get("/stats/by-store")
def get_store_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get spending summary by store."""
    query = db.query(models.Bill)

    # Apply date filters if provided
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
            query = query.filter(models.Bill.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
            query = query.filter(models.Bill.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    bills = query.all()

    # Group by store
    store_totals = {}
    no_store_total = 0.0

    for bill in bills:
        if bill.store_name:
            if bill.store_name not in store_totals:
                store_totals[bill.store_name] = {
                    "total": 0.0,
                    "bill_count": 0
                }
            store_totals[bill.store_name]["total"] += bill.total
            store_totals[bill.store_name]["bill_count"] += 1
        else:
            no_store_total += bill.total

    return {
        "stores": store_totals,
        "no_store": no_store_total,
        "total": sum(s["total"] for s in store_totals.values()) + no_store_total
    }
