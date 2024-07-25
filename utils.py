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


def call_openai_api(image_base64, openai_api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    payload = {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
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
