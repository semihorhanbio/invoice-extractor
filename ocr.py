from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

# import pytesseract
import json
from utils import extract_pdf, encode_image, call_openai_api
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

router = APIRouter()
groq_client = Groq(api_key=groq_api_key)


@router.post("/inference")
async def inference(file: UploadFile = File(...)):
    result = None
    if file:
        if file.content_type in ["image/jpeg", "image/jpg", "image/png"]:
            try:
                image_base64 = await encode_image(file)
                response = call_openai_api(
                    image_base64, openai_api_key, file.content_type.lower()
                )
                result = response["choices"][0]["message"]["content"]
                result = result.replace("```", "").replace("json", "")
                result = json.loads(result)
            except:
                return {"error": "Taranmış fatura işlenememektedir."}
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
