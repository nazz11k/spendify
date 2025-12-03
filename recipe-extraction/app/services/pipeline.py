import logging
import numpy as np
import cv2
from datetime import datetime
import re

from .detector import YoloService
from .ocr import OcrService
from .classifier import ClassifierService
from app.utils.text_cleaning import clean_amount, find_total_amount, clean_date, find_date_in_text
from app.api.schemas import ReceiptData

logger = logging.getLogger(__name__)


class ReceiptPipeline:
    def __init__(self):
        logger.info("Initializing Pipeline components...")
        try:
            self.detector = YoloService()
            self.ocr = OcrService()
            self.classifier = ClassifierService()
            logger.info("Pipeline is ready.")
        except Exception as e:
            logger.critical(f"Failed to initialize pipeline: {e}")
            raise e

    def process_image(self, image_bytes: bytes) -> ReceiptData:
        logger.info(f"Processing image ({len(image_bytes)} bytes)...")

        img_rgb = self._decode_image(image_bytes)

        results = self._detect_objects(img_rgb)

        extracted_data, full_invoice_text = self._extract_data_from_boxes(results, img_rgb)

        self._apply_fallback(extracted_data, full_invoice_text)

        extracted_data["category"] = self._classify(full_invoice_text)

        logger.info(f"Result: {extracted_data['amount']} "
                    f"| {extracted_data['date']} "
                    f"| {extracted_data['category']}")

        return ReceiptData(
            date=extracted_data["date"],
            amount=extracted_data["amount"],
            category=extracted_data["category"]
        )

    def _decode_image(self, image_bytes: bytes) -> np.ndarray:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image")

            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise ValueError("Invalid image format")

    def _detect_objects(self, img_rgb: np.ndarray):
        try:
            results = self.detector.detect(img_rgb)
            logger.info(f"YOLO detected {len(results.boxes)} objects.")
            return results
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            raise e

    def _extract_data_from_boxes(self, results, img_rgb: np.ndarray) -> tuple[dict, str]:
        extracted = {
            "date": None,
            "amount": 0.0,
            "category": "Other"
        }
        full_text_parts = []

        TARGET_CLASSES = ["invoice", "date", "sum"]
        h, w, _ = img_rgb.shape

        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.detector.CLASS_MAPPING.get(class_id)

            if class_name not in TARGET_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x1 >= x2 or y1 >= y2:
                continue

            crop = img_rgb[y1:y2, x1:x2]

            text = self.ocr.extract_text(crop)
            if not text.strip():
                continue

            clean_line = text.replace('\n', ' ').strip()

            if class_name == "sum":
                val = clean_amount(clean_line)
                if val > extracted["amount"]:
                    extracted["amount"] = val

            elif class_name == "date":
                date_val = clean_date(clean_line)
                if date_val:
                    extracted["date"] = date_val
                    logger.info(f"Date found in box: {date_val}")

            elif class_name == "invoice":
                full_text_parts.append(clean_line)

        return extracted, " ".join(full_text_parts)

    def _apply_fallback(self, extracted: dict, full_text: str):
        if not full_text:
            logger.warning("Invoice text not found (or OCR failed). Fallback search impossible.")
            if not extracted["date"]:
                extracted["date"] = datetime.now().strftime("%Y-%m-%d")
            return

        if not extracted["date"]:
            logger.info("Date not found in boxes. Searching in full text...")
            found_date = find_date_in_text(full_text)
            if found_date:
                extracted["date"] = found_date
                logger.info(f"Fallback: Date found -> {found_date}")
            else:
                today = datetime.now().strftime("%Y-%m-%d")
                logger.warning(f"Date not found anywhere. Using today: {today}")
                extracted["date"] = today

        if extracted["amount"] == 0.0:
            logger.info("Amount not found in boxes. Searching in full text...")
            found_amount = find_total_amount(full_text)
            if found_amount > 0:
                extracted["amount"] = found_amount
                logger.info(f"Fallback: Amount found -> {found_amount}")
            else:
                logger.warning("Fallback: Amount not found in text.")

    def _classify(self, full_text: str) -> str:
        if not full_text:
            return "Other"

        text_for_ai = full_text.strip()[:1500]
        text_for_ai = re.sub(r'\d+', '', text_for_ai)

        try:
            category = self.classifier.predict_category(text_for_ai)
            logger.info(f"Classification result: {category}")
            return category
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "Other"
