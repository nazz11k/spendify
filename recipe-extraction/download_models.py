import os
import logging
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.core.config import settings
from app.core.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def download_paddle():
    models_map = {
        settings.DET_MODEL_DIR: "PaddlePaddle/PP-OCRv5_server_det",
        settings.REC_MODEL_DIR: "PaddlePaddle/en_PP-OCRv5_mobile_rec",
        settings.CLS_MODEL_DIR: "PaddlePaddle/PP-LCNet_x1_0_textline_ori"
    }

    for local_dir, repo_id in models_map.items():
        if os.path.exists(local_dir) and any(f.endswith(".pdmodel") for f in os.listdir(local_dir)):
            logger.info(f"Model {repo_id} already exists in {local_dir}")
            continue

        logger.info(f"Downloading {repo_id} from Hugging Face...")
        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                allow_patterns=["*.pdmodel", "*.pdiparams", "*.yml", "*.yaml", "*.json"]
            )
            logger.info(f"Successful: {repo_id}")
        except Exception as e:
            logger.error(f"Error during downloading {repo_id}: {e}")


def download_bert():
    output_dir = settings.BERT_MODEL_PATH
    if os.path.exists(output_dir) and any(f.endswith(".json") for f in os.listdir(output_dir)):
        logger.info(f"BERT model already exists at {output_dir}")
        return

    logger.info("Downloading BERT model...")
    model_name = "cross-encoder/nli-distilroberta-base"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        tokenizer.save_pretrained(output_dir)
        model.save_pretrained(output_dir)
        logger.info(f"BERT saved to {output_dir}")
    except Exception as e:
        logger.error(f"Failed to download BERT: {e}")


def check_yolo():
    if not os.path.exists(settings.YOLO_MODEL_PATH):
        logger.warning(f"YOLO model NOT FOUND at {settings.YOLO_MODEL_PATH}")
    else:
        logger.info("YOLO model found.")


def prepare_dirs():
    if not os.path.exists(settings.MODELS_DIR):
        os.makedirs(settings.MODELS_DIR)


if __name__ == "__main__":
    prepare_dirs()
    check_yolo()
    download_bert()
    download_paddle()
