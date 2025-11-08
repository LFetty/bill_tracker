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
    def extract_store_name(text: str) -> Optional[str]:
        """
        Extract store name from receipt text.
        Store name is typically in the first few lines.
        """
        lines = text.strip().split('\n')

        # Look at first 5 lines for store name
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            # Skip empty lines and lines with common receipt headers
            if not line or len(line) < 3:
                continue
            # Skip lines that look like addresses (contain numbers and street indicators)
            if re.search(r'\d+.*\b(street|st|road|rd|avenue|ave|blvd|lane|ln)\b', line, re.IGNORECASE):
                continue
            # Skip lines that look like phone numbers
            if re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line):
                continue
            # Skip lines with only numbers or dates
            if re.match(r'^[\d\s\-/:.]+$', line):
                continue
            # If we find a line with mostly letters and some length, use it as store name
            if len(line) >= 3 and len(line) <= 50 and re.search(r'[a-zA-Z]', line):
                return line

        return None

    @staticmethod
    def parse_bill_items(text: str) -> Tuple[List[Tuple[str, float]], Optional[float], Optional[str]]:
        """
        Parse bill text to extract items, prices, and store name.
        Returns: (list of (product_name, amount) tuples, total_amount, store_name)
        """
        items = []
        total = None

        # Split text into lines
        lines = text.strip().split('\n')

        # Extract store name
        store_name = OCRService.extract_store_name(text)

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

        return items, total, store_name

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

    @staticmethod
    def auto_categorize_item(product_name: str, item_keywords_map: dict) -> Optional[int]:
        """
        Auto-categorize a product to an item based on item keywords.
        item_keywords_map: {item_id: [list of keywords]}
        Returns: item_id or None
        """
        product_lower = product_name.lower()

        # Check each item's keywords for exact or partial match
        best_match = None
        best_match_length = 0

        for item_id, keywords in item_keywords_map.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check for exact match or if keyword is in product name
                if keyword_lower == product_lower or keyword_lower in product_lower:
                    # Prefer longer keyword matches (more specific)
                    if len(keyword_lower) > best_match_length:
                        best_match = item_id
                        best_match_length = len(keyword_lower)

        return best_match
