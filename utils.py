import fitz  # pymupdf
import shutil
import os
import base64
import requests


def save_file_to_server(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as + extension)

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return temp_file


def extract_pdf(file_bytes):
    """
    Extracts text from a PDF file.

    :param file_bytes: The bytes of the PDF file.
    :return: A string containing the extracted text.
    """
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
        return text


# Function to encode the image
async def encode_image(file):
    image = await file.read()
    return base64.b64encode(image).decode("utf-8")


def call_openai_api(image_base64, openai_api_key, img_type):
    prompt = """
Convert the invoice data from the image into JSON format. If the required information is not found, set it as "no value". The required properties in the JSON object are as follows:

Invoice = {
    "customer_name": str,
    "customer_vkn": int,
    "customer_tckn": int,
    "vendor_name": str,
    "vendor_vkn": int,
    "vendor_tckn": int,
    "invoice_senario": str,
    "invoice_type": str,
    "invoice_no": str,
    "invoice_date": date,
    "total_of_goods_and_services": float,
    "calculated_vat": float,
    "invoice_total": float,
    "invoice_lines": list[goods_and_services_name: str, goods_and_services_quantity: int, goods_and_services_unit_price: float, goods_and_services_vat_rate: float, goods_and_services_total: float]
}
"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{img_type};base64,{image_base64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    return response.json()


""" def invoke_ocr(img_path: str) -> str:
    try:
        text = pytesseract.image_to_string(img_path)
        return text
    except:
        return "[ERROR] Unable to process file: {0}".format(img_path) """
