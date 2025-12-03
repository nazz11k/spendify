import logging
import os
from paddleocr import PaddleOCR

from app.core.config import settings

logger = logging.getLogger(__name__)


class OcrService:
    def __init__(self):
        logger.info("Loading PaddleOCR with Hugging Face models...")

        if not os.path.exists(settings.DET_MODEL_DIR):
            logger.error(f"CRITICAL: Detection model missing in {settings.DET_MODEL_DIR}")
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            det_model_dir=settings.DET_MODEL_DIR,
            rec_model_dir=settings.REC_MODEL_DIR,
            cls_model_dir=settings.CLS_MODEL_DIR,
        )

    def extract_text(self, image_crop) -> str:
        try:
            result = self.ocr.ocr(image_crop)

            if not result:
                return ""

            res_data = result[0]

            if res_data is None:
                return ""

            if isinstance(res_data, dict) and 'rec_texts' in res_data:
                text_list = res_data['rec_texts']
                valid_texts = [t for t in text_list if t]
                text = "\n".join(valid_texts)
                return text

            elif isinstance(res_data, list):
                lines = []
                for line in res_data:
                    if isinstance(line, list) and len(line) >= 2 and isinstance(line[1], tuple):
                        lines.append(line[1][0])
                return "\n".join(lines)

            return ""

        except Exception as e:
            logger.warning(f"OCR failed on crop: {e}")
            return ""
