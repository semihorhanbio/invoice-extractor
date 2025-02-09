from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from utils import encode_image, extract_pdf
from services.invoice_extraction import (
    extract_invoice_data_from_image,
    extract_invoice_data_from_pdf,
)
from services.receipt_extraction import (
    extract_receipt_data,
    extract_receipt_data_from_pdf,
)
from config import OPENAI_API_KEY

router = APIRouter()


@router.post("/extract-invoice")
async def inference(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        if file.content_type in ["image/jpeg", "image/png"]:
            image_base64 = await encode_image(file)
            response = extract_invoice_data_from_image(
                image_base64, OPENAI_API_KEY, file.content_type
            )
        elif file.content_type == "application/pdf":
            pdf_bytes = await file.read()
            text = extract_pdf(pdf_bytes)
            response = extract_invoice_data_from_pdf(text, OPENAI_API_KEY)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPG, PNG, and PDF are allowed.",
            )
        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-receipt")
async def extract_receipt(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        if file.content_type in ["image/jpeg", "image/png"]:
            image_base64 = await encode_image(file)
            response = extract_receipt_data(
                image_base64, OPENAI_API_KEY, file.content_type
            )
        elif file.content_type == "application/pdf":
            pdf_bytes = await file.read()
            text = extract_pdf(pdf_bytes)
            response = extract_receipt_data_from_pdf(text, OPENAI_API_KEY)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPG, PNG, and PDF are allowed.",
            )
        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
