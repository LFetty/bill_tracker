import pytesseract
from PIL import Image
import re
from typing import List, Tuple, Optional


class OCRService:
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """Extract text from an image using Tesseract OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    @staticmethod
    def parse_bill_items(text: str) -> Tuple[List[Tuple[str, float]], Optional[float]]:
        """
        Parse bill text to extract items and prices.
        Returns: (list of (product_name, amount) tuples, total_amount)
        """
        items = []
        total = None

        # Split text into lines
        lines = text.strip().split('\n')

        # Pattern to match price (e.g., 12.99, $12.99, 12,99, €12.99)
        price_pattern = r'[\$€£]?\s*(\d+[.,]\d{2})\s*[\$€£]?'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for "TOTAL" or "SUM" or "GESAMT" lines
            if re.search(r'\b(TOTAL|SUM|GESAMT|SUMME)\b', line, re.IGNORECASE):
                # Extract the total amount
                match = re.search(price_pattern, line)
                if match:
                    total = float(match.group(1).replace(',', '.'))
                continue

            # Try to find lines with both text and a price
            match = re.search(price_pattern, line)
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    price = float(price_str)
                    # Extract product name (text before the price)
                    product_name = line[:match.start()].strip()
                    # Clean up common artifacts
                    product_name = re.sub(r'\s+', ' ', product_name)
                    product_name = product_name.strip('.-_*#')

                    if product_name and len(product_name) > 2:
                        items.append((product_name, price))
                except ValueError:
                    continue

        return items, total

    @staticmethod
    def auto_categorize(product_name: str, keywords_map: dict) -> Optional[int]:
        """
        Auto-categorize a product based on keywords.
        keywords_map: {subcategory_id: [list of keywords]}
        Returns: subcategory_id or None
        """
        product_lower = product_name.lower()

        # Check each subcategory's keywords
        for subcategory_id, keywords in keywords_map.items():
            for keyword in keywords:
                if keyword.lower() in product_lower:
                    return subcategory_id

        return None
