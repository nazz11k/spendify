import logging
from transformers import pipeline
from app.core.config import settings

logger = logging.getLogger(__name__)


class ClassifierService:
    def __init__(self):
        logger.info(f"Loading Zero-Shot Classifier from {settings.BERT_MODEL_PATH}...")
        try:
            self.pipeline = pipeline(
                "zero-shot-classification",
                model=settings.BERT_MODEL_PATH,
                tokenizer=settings.BERT_MODEL_PATH
            )
            logger.info("Classifier loaded.")
        except Exception as e:
            logger.critical(f"Failed to load BERT model: {e}")
            raise e

    def predict_category(self, text: str) -> str:
        if len(text) < 3:
            return "Other"

        try:
            result = self.pipeline(text,
                                   candidate_labels=settings.CANDIDATE_LABELS,
                                   hypothesis_template="This is a receipt for {} products.",
                                   )
            return result['labels'][0]
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return "Other"
