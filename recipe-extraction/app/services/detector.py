import logging
import os
import torch
from ultralytics import YOLO
from app.core.config import settings

logger = logging.getLogger(__name__)


class YoloService:
    def __init__(self):
        if not os.path.exists(settings.YOLO_MODEL_PATH):
            logger.error(f"YOLO model missing at {settings.YOLO_MODEL_PATH}")
            raise FileNotFoundError("YOLO model not found")

        logger.info(f"Loading YOLO model from {settings.YOLO_MODEL_PATH}...")
        _original_load = torch.load

        def safe_load(*args, **kwargs):
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return _original_load(*args, **kwargs)

        torch.load = safe_load

        try:
            self.model = YOLO(settings.YOLO_MODEL_PATH)
        finally:
            torch.load = _original_load

        self.CLASS_MAPPING = {
            0: 'Item list',
            1: 'Merchant name',
            2: 'address',
            3: 'date',
            4: 'invoice',
            5: 'payment information',
            6: 'price',
            7: 'sum',
            8: 'tax information'
        }

    def detect(self, image):
        logger.debug("Running YOLO detection inference...")
        return self.model(image, conf=0.25, verbose=False)[0]
