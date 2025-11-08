from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from ..database import get_db
from ..models import models, schemas
from ..services.ocr_service import OCRService

router = APIRouter(prefix="/ocr", tags=["ocr"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/scan", response_model=schemas.OCRResponse)
async def scan_bill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a bill image and extract text using OCR.
    Returns extracted items with suggested categorization.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text using OCR
        ocr_service = OCRService()
        raw_text = ocr_service.extract_text_from_image(file_path)

        # Parse bill items
        parsed_items, total, store_name = ocr_service.parse_bill_items(raw_text)

        # Build keywords map for auto-categorization
        subcategories = db.query(models.Subcategory).all()
        keywords_map = {}
        for subcat in subcategories:
            keywords_map[subcat.id] = [kw.keyword for kw in subcat.keywords]

        # Auto-categorize items
        ocr_items = []
        for product_name, amount in parsed_items:
            suggested_subcat_id = ocr_service.auto_categorize(product_name, keywords_map)
            ocr_items.append(schemas.OCRItem(
                product_name=product_name,
                amount=amount,
                suggested_subcategory_id=suggested_subcat_id
            ))

        return schemas.OCRResponse(
            items=ocr_items,
            total=total,
            store_name=store_name,
            raw_text=raw_text
        )

    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.post("/scan-and-save", response_model=schemas.Bill)
async def scan_and_save_bill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a bill image, extract text using OCR, and save as a new bill.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text using OCR
        ocr_service = OCRService()
        raw_text = ocr_service.extract_text_from_image(file_path)

        # Parse bill items
        parsed_items, total, store_name = ocr_service.parse_bill_items(raw_text)

        # Build keywords map for auto-categorization
        subcategories = db.query(models.Subcategory).all()
        keywords_map = {}
        for subcat in subcategories:
            keywords_map[subcat.id] = [kw.keyword for kw in subcat.keywords]

        # Create bill
        db_bill = models.Bill(
            total=total or 0.0,
            store_name=store_name,
            image_path=file_path,
            notes=f"Auto-imported via OCR"
        )
        db.add(db_bill)
        db.flush()

        # Add bill items with auto-categorization
        calculated_total = 0.0
        for product_name, amount in parsed_items:
            suggested_subcat_id = ocr_service.auto_categorize(product_name, keywords_map)
            db_item = models.BillItem(
                bill_id=db_bill.id,
                product_name=product_name,
                amount=amount,
                subcategory_id=suggested_subcat_id
            )
            db.add(db_item)
            calculated_total += amount

        # Update total if not extracted
        if not total:
            db_bill.total = calculated_total

        db.commit()
        db.refresh(db_bill)
        return db_bill

    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
