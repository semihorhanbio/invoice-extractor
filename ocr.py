from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
#import pytesseract
import json
import base64
import requests
from utils import extract_pdf, save_file_to_server
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

router = APIRouter()
groq_client = Groq(api_key=groq_api_key)

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

def call_openai_api(image_base64):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "response_format": { "type": "json_object" },
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a specialist in comprehending invoices. Input files in the form of invoices will be provided to you, and your task is to convert invoice data into json format. If the requirement information is not found, set "no value". The required properties in JSON object are as follows.\n  Invoice = {"customer_name": str, "customer_vkn": int, customer_tckn": int, "vendor_name": str, "vendor_vkn": int, vendor_tckn": int, invoice_senario: str, invoice_type: str, invoice_no: str, invoice_date: date, total_of_goods_and_services: float, calculated_vat: float, invoice_total: float, invoice_lines: list[goods_and_services_name: str, goods_and_services_quantity: int, goods_and_services_unit_price: float, goods_and_services_vat_rate: float, goods_and_services_total: float]}\n  Return just a `Invoice` in json format no additional info."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def invoke_ocr(img_path: str) -> str:
    """
    Extract text from an image using tesseract
    """
    try:
        text = pytesseract.image_to_string(img_path)
        return text
    except:
        return "[ERROR] Unable to process file: {0}".format(img_path)


@router.post("/inference")
async def inference(file: UploadFile = File(...)):
    result = None
    if file:
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]:
            print("Images Uploaded: ", file.filename)
            image_base64 = encode_image(file)
            response = call_openai_api(image_base64)
            result = json.loads( response.choices[0].message.content)
            return JSONResponse(content=result, media_type="application/json")
        elif file.content_type == "application/pdf":
            pdf_bytes = await file.read()
            text = extract_pdf(pdf_bytes)
        else:
            return {
                "error": "Invalid file type. Only JPG/PNG images and PDF are allowed."
            }

        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": 'You are a specialist in comprehending invoices. Input files in the form of invoices will be provided to you, and your task is to convert invoice data into json format. If the requirement information is not found, set "no value". The required properties in JSON object are as follows.\n  Invoice = {"customer_name": str, "customer_vkn": int, customer_tckn": int, "vendor_name": str, "vendor_vkn": int, vendor_tckn": int, invoice_senario: str, invoice_type: str, invoice_no: str, invoice_date: date, total_of_goods_and_services: float, calculated_vat: float, invoice_total: float, invoice_lines: list[goods_and_services_name: str, goods_and_services_quantity: int, goods_and_services_unit_price: float, goods_and_services_vat_rate: float, goods_and_services_total: float]}\n  Return just a `Invoice` in json format no additional info.',
                },
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
            response_format={"type": "json_object"},
        )
        result = completion.choices[0].message.content
        result = json.loads(result)

    else:
        result = {"info": "No input provided"}

    if result is None:
        raise HTTPException(status_code=400, detail=f"Failed to process the input.")

    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
