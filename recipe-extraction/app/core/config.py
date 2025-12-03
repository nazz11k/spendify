import os


class Settings:
    PROJECT_NAME: str = "Receipt Extraction Service"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR = os.path.join(BASE_DIR, "models")

    YOLO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8", "best.pt")
    BERT_MODEL_PATH = os.path.join(MODELS_DIR, "bert")

    PADDLE_BASE_DIR = os.path.join(MODELS_DIR, "paddleocr")

    DET_MODEL_DIR = os.path.join(PADDLE_BASE_DIR, "det_server_v5")
    REC_MODEL_DIR = os.path.join(PADDLE_BASE_DIR, "rec_mobile_v5_en")
    CLS_MODEL_DIR = os.path.join(PADDLE_BASE_DIR, "cls_textline_v1")

    RECEIPT_EXTRACTOR_API_HOST = os.getenv("RECEIPT_EXTRACTOR_API_HOST", "127.0.0.1")
    RECEIPT_EXTRACTOR_API_PORT = os.getenv("RECEIPT_EXTRACTOR_API_PORT", "8001")

    _labels_str = os.getenv(
        "DEFAULT_LABELS",
        "Groceries,Transport,Restaurants,Health,Electronics,Entertainment"
    )

    CANDIDATE_LABELS = [label.strip() for label in _labels_str.split(",")]


settings = Settings()
