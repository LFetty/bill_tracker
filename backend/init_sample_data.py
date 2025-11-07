"""
Script to initialize the database with sample categories and subcategories.
Run this after setting up the backend to get started quickly.
"""

from app.database import SessionLocal, engine
from app.models.models import Base, Category, Subcategory, CategoryKeyword

# Create tables
Base.metadata.create_all(bind=engine)

# Sample data structure
SAMPLE_CATEGORIES = [
    {
        "name": "Mobility",
        "description": "Transportation and vehicle expenses",
        "subcategories": [
            {
                "name": "Car",
                "description": "Car-related expenses",
                "keywords": ["gas", "fuel", "petrol", "gasoline", "car wash", "parking", "garage", "mechanic", "oil change"]
            },
            {
                "name": "Public Transport",
                "description": "Public transportation expenses",
                "keywords": ["bus", "train", "metro", "subway", "tram", "ticket", "transit", "fare"]
            },
            {
                "name": "Taxi & Rideshare",
                "description": "Taxi and rideshare services",
                "keywords": ["uber", "lyft", "taxi", "cab", "rideshare"]
            }
        ]
    },
    {
        "name": "Food & Dining",
        "description": "Food and restaurant expenses",
        "subcategories": [
            {
                "name": "Groceries",
                "description": "Grocery shopping",
                "keywords": ["grocery", "supermarket", "market", "produce", "vegetables", "fruits", "meat", "dairy"]
            },
            {
                "name": "Restaurants",
                "description": "Dining out",
                "keywords": ["restaurant", "cafe", "diner", "bistro", "eatery", "dining"]
            },
            {
                "name": "Fast Food",
                "description": "Fast food and takeout",
                "keywords": ["mcdonalds", "burger", "pizza", "subway", "kfc", "taco", "wendy", "fast food"]
            }
        ]
    },
    {
        "name": "Shopping",
        "description": "Shopping and retail expenses",
        "subcategories": [
            {
                "name": "Clothing",
                "description": "Clothing and apparel",
                "keywords": ["clothes", "shirt", "pants", "shoes", "dress", "jacket", "apparel", "fashion"]
            },
            {
                "name": "Electronics",
                "description": "Electronic devices and accessories",
                "keywords": ["phone", "computer", "laptop", "tablet", "headphones", "electronics", "tech", "cable"]
            },
            {
                "name": "Home & Garden",
                "description": "Home improvement and garden supplies",
                "keywords": ["furniture", "decor", "garden", "tools", "hardware", "home depot", "ikea"]
            }
        ]
    },
    {
        "name": "Utilities",
        "description": "Utility bills and services",
        "subcategories": [
            {
                "name": "Electricity",
                "description": "Electric utility bills",
                "keywords": ["electric", "electricity", "power", "energy"]
            },
            {
                "name": "Water",
                "description": "Water utility bills",
                "keywords": ["water", "sewer", "wastewater"]
            },
            {
                "name": "Internet & Phone",
                "description": "Internet and phone services",
                "keywords": ["internet", "wifi", "broadband", "phone", "mobile", "cellular"]
            }
        ]
    },
    {
        "name": "Entertainment",
        "description": "Entertainment and leisure expenses",
        "subcategories": [
            {
                "name": "Movies & Streaming",
                "description": "Movies and streaming services",
                "keywords": ["netflix", "cinema", "movie", "hulu", "disney", "prime video", "streaming"]
            },
            {
                "name": "Sports & Fitness",
                "description": "Sports and fitness activities",
                "keywords": ["gym", "fitness", "yoga", "sports", "workout", "exercise"]
            },
            {
                "name": "Hobbies",
                "description": "Hobby-related expenses",
                "keywords": ["hobby", "craft", "art", "music", "books", "games"]
            }
        ]
    },
    {
        "name": "Healthcare",
        "description": "Medical and healthcare expenses",
        "subcategories": [
            {
                "name": "Pharmacy",
                "description": "Medication and pharmacy",
                "keywords": ["pharmacy", "medicine", "prescription", "drug", "medication"]
            },
            {
                "name": "Doctor Visits",
                "description": "Medical appointments",
                "keywords": ["doctor", "clinic", "hospital", "medical", "physician"]
            },
            {
                "name": "Dental",
                "description": "Dental care",
                "keywords": ["dental", "dentist", "teeth", "orthodontist"]
            }
        ]
    }
]


def init_sample_data():
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(Category).first()
        if existing:
            print("Database already has data. Skipping initialization.")
            print("To reset, delete the bill_tracker.db file and run this script again.")
            return

        print("Initializing database with sample categories...")

        for cat_data in SAMPLE_CATEGORIES:
            # Create category
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(category)
            db.flush()

            print(f"  Created category: {category.name}")

            # Create subcategories
            for subcat_data in cat_data["subcategories"]:
                subcategory = Subcategory(
                    name=subcat_data["name"],
                    description=subcat_data["description"],
                    category_id=category.id
                )
                db.add(subcategory)
                db.flush()

                print(f"    Created subcategory: {subcategory.name}")

                # Create keywords
                for keyword in subcat_data["keywords"]:
                    kw = CategoryKeyword(
                        subcategory_id=subcategory.id,
                        keyword=keyword
                    )
                    db.add(kw)

                print(f"      Added {len(subcat_data['keywords'])} keywords")

        db.commit()
        print("\nDatabase initialized successfully!")
        print("You can now start the application and begin tracking bills.")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()
