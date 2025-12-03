import uvicorn
import os
import sys
import logging

from app.core.config import settings

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))

    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    try:
        from app.main import app
        uvicorn.run(app,
                    host=settings.RECEIPT_EXTRACTOR_API_HOST,
                    port=int(settings.RECEIPT_EXTRACTOR_API_PORT)
                    )

    except ImportError as e:
        logging.error(f"ImportError: {e}")
