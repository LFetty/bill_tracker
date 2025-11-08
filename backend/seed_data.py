"""
Seed script to populate the database with test data.
This script creates categories, subcategories, and bills with items
for testing the dashboard features.
"""

import sys
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import models

# Seed data structure
SEED_DATA = {
    "Groceries": {
        "subcategories": ["Dairy", "Meat", "Vegetables", "Fruits", "Bakery", "Beverages"],
        "items": {
            "Dairy": ["Milk", "Cheese", "Yogurt", "Butter", "Cream"],
            "Meat": ["Chicken Breast", "Ground Beef", "Pork Chops", "Salmon", "Turkey"],
            "Vegetables": ["Tomatoes", "Lettuce", "Carrots", "Broccoli", "Onions"],
            "Fruits": ["Apples", "Bananas", "Oranges", "Grapes", "Strawberries"],
            "Bakery": ["Bread", "Croissants", "Bagels", "Muffins", "Donuts"],
            "Beverages": ["Orange Juice", "Coffee", "Tea", "Soda", "Water"]
        }
    },
    "Mobility": {
        "subcategories": ["Fuel", "Public Transport", "Parking", "Car Maintenance", "Taxi/Rideshare"],
        "items": {
            "Fuel": ["Gasoline", "Diesel"],
            "Public Transport": ["Metro Card", "Bus Ticket", "Train Ticket"],
            "Parking": ["Parking Fee", "Parking Meter"],
            "Car Maintenance": ["Oil Change", "Tire Rotation", "Car Wash", "Air Filter"],
            "Taxi/Rideshare": ["Uber Ride", "Taxi Fare", "Lyft Ride"]
        }
    },
    "Presents": {
        "subcategories": ["Birthday", "Anniversary", "Holiday", "Wedding", "Baby Shower"],
        "items": {
            "Birthday": ["Birthday Card", "Gift Wrap", "Cake", "Flowers"],
            "Anniversary": ["Flowers", "Chocolate", "Wine", "Jewelry"],
            "Holiday": ["Christmas Gift", "Holiday Card", "Decorations"],
            "Wedding": ["Wedding Gift", "Card", "Gift Wrap"],
            "Baby Shower": ["Baby Clothes", "Toys", "Diapers", "Gift Card"]
        }
    },
    "Home": {
        "subcategories": ["Utilities", "Furniture", "Cleaning Supplies", "Garden", "Repairs"],
        "items": {
            "Utilities": ["Electricity Bill", "Water Bill", "Gas Bill", "Internet Bill"],
            "Furniture": ["Chair", "Table", "Lamp", "Shelf", "Desk"],
            "Cleaning Supplies": ["Detergent", "Paper Towels", "Trash Bags", "Cleaner", "Sponges"],
            "Garden": ["Plants", "Soil", "Seeds", "Garden Tools", "Fertilizer"],
            "Repairs": ["Plumbing", "Electrical", "Paint", "Tools", "Hardware"]
        }
    },
    "Healthcare": {
        "subcategories": ["Pharmacy", "Doctor Visit", "Dental", "Vision", "Supplements"],
        "items": {
            "Pharmacy": ["Pain Reliever", "Vitamins", "Cold Medicine", "Bandages", "First Aid Kit"],
            "Doctor Visit": ["Co-pay", "Lab Work", "X-Ray"],
            "Dental": ["Cleaning", "Filling", "Toothbrush", "Toothpaste", "Floss"],
            "Vision": ["Eye Exam", "Glasses", "Contact Lenses", "Eye Drops"],
            "Supplements": ["Multivitamin", "Vitamin D", "Omega-3", "Protein Powder"]
        }
    },
    "Entertainment": {
        "subcategories": ["Movies", "Music", "Sports", "Hobbies", "Dining Out"],
        "items": {
            "Movies": ["Movie Ticket", "Popcorn", "Streaming Subscription"],
            "Music": ["Concert Ticket", "Music Subscription", "Vinyl Record"],
            "Sports": ["Gym Membership", "Sports Equipment", "Game Ticket"],
            "Hobbies": ["Art Supplies", "Books", "Games", "Craft Materials"],
            "Dining Out": ["Restaurant Meal", "Fast Food", "Coffee Shop", "Pizza"]
        }
    }
}

# Store names for generating bills
STORES = {
    "Groceries": ["Walmart", "Target", "Whole Foods", "Kroger", "Safeway"],
    "Mobility": ["Shell", "BP", "Chevron", "ExxonMobil", "76 Station"],
    "Presents": ["Amazon", "Target", "Walmart", "Macy's", "Nordstrom"],
    "Home": ["Home Depot", "Lowe's", "IKEA", "Bed Bath & Beyond", "Target"],
    "Healthcare": ["CVS", "Walgreens", "Rite Aid", "Walmart Pharmacy", "Target Pharmacy"],
    "Entertainment": ["AMC Theaters", "Spotify", "Netflix", "Barnes & Noble", "GameStop"]
}

# Price ranges for items (min, max)
PRICE_RANGES = {
    "Groceries": (1.5, 25.0),
    "Mobility": (3.0, 80.0),
    "Presents": (10.0, 150.0),
    "Home": (5.0, 200.0),
    "Healthcare": (5.0, 100.0),
    "Entertainment": (8.0, 60.0)
}


def clear_database(db: Session):
    """Clear all existing data from the database."""
    print("Clearing existing data...")
    db.query(models.BillItem).delete()
    db.query(models.Bill).delete()
    db.query(models.CategoryKeyword).delete()
    db.query(models.Subcategory).delete()
    db.query(models.Category).delete()
    db.commit()
    print("Database cleared.")


def create_categories(db: Session):
    """Create categories and subcategories."""
    print("\nCreating categories and subcategories...")
    category_map = {}
    subcategory_map = {}

    for category_name, data in SEED_DATA.items():
        # Create category
        category = models.Category(
            name=category_name,
            description=f"{category_name} expenses"
        )
        db.add(category)
        db.flush()
        category_map[category_name] = category
        subcategory_map[category_name] = {}

        # Create subcategories
        for subcat_name in data["subcategories"]:
            subcategory = models.Subcategory(
                name=subcat_name,
                category_id=category.id,
                description=f"{subcat_name} items"
            )
            db.add(subcategory)
            db.flush()
            subcategory_map[category_name][subcat_name] = subcategory

            # Add keywords for items
            for item_name in data["items"][subcat_name]:
                keyword = models.CategoryKeyword(
                    subcategory_id=subcategory.id,
                    keyword=item_name.lower()
                )
                db.add(keyword)

    db.commit()
    print(f"Created {len(category_map)} categories and {sum(len(s) for s in subcategory_map.values())} subcategories")
    return category_map, subcategory_map


def generate_bills(db: Session, subcategory_map, months_back=3):
    """Generate bills for the last N months."""
    print(f"\nGenerating bills for the last {months_back} months...")

    bills_created = 0
    items_created = 0

    # Generate bills for each month
    for month_offset in range(months_back):
        # Calculate date range for this month
        current_date = datetime.now()
        target_date = current_date - timedelta(days=30 * month_offset)
        month_start = datetime(target_date.year, target_date.month, 1)

        # Get the last day of the month
        if target_date.month == 12:
            month_end = datetime(target_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(target_date.year, target_date.month + 1, 1) - timedelta(days=1)

        print(f"\n  Generating bills for {month_start.strftime('%B %Y')}...")

        # Generate 8-15 bills per month
        num_bills = random.randint(8, 15)

        for _ in range(num_bills):
            # Pick a random category
            category_name = random.choice(list(SEED_DATA.keys()))
            subcats = list(subcategory_map[category_name].keys())

            # Pick 1-3 subcategories for this bill
            num_subcats = random.randint(1, min(3, len(subcats)))
            selected_subcats = random.sample(subcats, num_subcats)

            # Pick a store
            store_name = random.choice(STORES[category_name])

            # Generate random date within the month
            days_in_month = (month_end - month_start).days
            random_day = random.randint(0, days_in_month)
            bill_date = month_start + timedelta(days=random_day,
                                                hours=random.randint(8, 20),
                                                minutes=random.randint(0, 59))

            # Create bill
            bill = models.Bill(
                date=bill_date,
                store_name=store_name,
                total=0.0,
                notes=f"{category_name} shopping at {store_name}"
            )
            db.add(bill)
            db.flush()
            bills_created += 1

            # Add items to bill
            bill_total = 0.0
            for subcat_name in selected_subcats:
                subcategory = subcategory_map[category_name][subcat_name]
                available_items = SEED_DATA[category_name]["items"][subcat_name]

                # Add 1-3 items from this subcategory
                num_items = random.randint(1, min(3, len(available_items)))
                selected_items = random.sample(available_items, num_items)

                for item_name in selected_items:
                    # Generate price within range
                    price_min, price_max = PRICE_RANGES[category_name]
                    # Add some variation to prices for same items
                    base_price = random.uniform(price_min, price_max)
                    price = round(base_price, 2)

                    bill_item = models.BillItem(
                        bill_id=bill.id,
                        product_name=item_name,
                        amount=price,
                        subcategory_id=subcategory.id
                    )
                    db.add(bill_item)
                    bill_total += price
                    items_created += 1

            # Update bill total
            bill.total = round(bill_total, 2)

        db.commit()
        print(f"    Created {num_bills} bills for {month_start.strftime('%B %Y')}")

    print(f"\nTotal bills created: {bills_created}")
    print(f"Total items created: {items_created}")


def seed_database():
    """Main function to seed the database."""
    print("=" * 60)
    print("BILL TRACKER - DATABASE SEED SCRIPT")
    print("=" * 60)

    # Create database tables
    print("\nCreating database tables...")
    models.Base.metadata.create_all(bind=engine)

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)

        # Create categories and subcategories
        category_map, subcategory_map = create_categories(db)

        # Generate bills with items
        generate_bills(db, subcategory_map, months_back=3)

        print("\n" + "=" * 60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Start the backend server: cd backend && uvicorn app.main:app --reload")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. View the dashboard with monthly expenses and store comparisons!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
