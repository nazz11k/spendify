from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.schemas import ReceiptResponse

router = APIRouter()


@router.post("/process/", response_model=ReceiptResponse)
async def process_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        contents = await file.read()

        from app.main import receipt_pipeline

        data = receipt_pipeline.process_image(contents)

        return ReceiptResponse(status="success", data=data)

    except Exception as e:
        return ReceiptResponse(
            status="error",
            data={},
            error=str(e)
        )
