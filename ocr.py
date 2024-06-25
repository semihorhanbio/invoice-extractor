from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
from functools import lru_cache
from paddleocr import PaddleOCR
from PIL import Image
import urllib.request
from io import BytesIO
import os
import time
import io
from utils import extract_pdf
from groq import Groq 


router = APIRouter()
client = Groq(api_key="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")


@lru_cache(maxsize=1)
def load_ocr_model():
    model = PaddleOCR(use_angle_cls=True, lang='en')
    return model


def merge_data(values):
    data = []
    for idx in range(len(values)):
        data.append([values[idx][1][0]])
        # print(data[idx])

    return data


def invoke_ocr(doc, content_type):
    worker_pid = os.getpid()
    print(f"Handling OCR request with worker PID: {worker_pid}")
    start_time = time.time()

    model = load_ocr_model()

    bytes_img = io.BytesIO()

    format_img = "JPEG"
    if content_type == "image/png":
        format_img = "PNG"

    doc.save(bytes_img, format=format_img)
    bytes_data = bytes_img.getvalue()
    bytes_img.close()

    result = model.ocr(bytes_data, cls=True)

    values = []
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            values.append(line)

    values = merge_data(values)

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"OCR done, worker PID: {worker_pid}")

    return values, processing_time


@router.post("/inference")
async def inference(file: Optional[UploadFile] = File(None), image_url: Optional[str] = Form(None)):
    result = None
    if file:
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]:
            doc = Image.open(BytesIO(await file.read()))
            text, processing_time = invoke_ocr(doc, file.content_type)
        elif file.content_type == "application/pdf":
            pdf_bytes = await file.read()
            text = extract_pdf(pdf_bytes)
        else:
            return {"error": "Invalid file type. Only JPG/PNG images and PDF are allowed."}

        completion = client.chat.completions.create(
    model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are a specialist in comprehending invoices. Input files in the form of invoices will be provided to you, and your task is to convert invoice data into json format. If the requirement information is not found, set \"no value\". The required properties in JSON object are as follows.\n  Invoice = {\"customer_name\": str, \"customer_vkn\": int, customer_tckn\": int, \"vendor_name\": str, \"vendor_vkn\": int, vendor_tckn\": int, invoice_senario: str, invoice_type: str, invoice_no: str, invoice_date: date, total_of_goods_and_services: float, calculated_vat: float, invoice_total: float, invoice_lines: list[goods_and_services_name: str, goods_and_services_quantity: int, goods_and_services_unit_price: float, goods_and_services_vat_rate: float, goods_and_services_total: float]}\n  Return just a `Invoice` in json format no additional info."
            },
            {
                "role": "user",
                "content": text
            },

        ],
        temperature=0.1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
)

        for chunk in completion:
            print(chunk.choices[0].delta.content or ""

        print(f"Processing time OCR: {processing_time:.2f} seconds")
        
    else:
        result = {"info": "No input provided"}

    if result is None:
        raise HTTPException(status_code=400, detail=f"Failed to process the input.")

    return JSONResponse(status_code=status.HTTP_200_OK, content=result)