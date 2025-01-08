import fitz  # pymupdf
import shutil
import os
import base64
from fastapi import UploadFile
import json


def generate_schema_string(schema_class):
    """
    Dynamically generates the JSON schema string from the Pydantic model.
    """
    schema = schema_class.model_json_schema()
    return f"""
The JSON object must adhere to the following schema:

{json.dumps(schema, indent=2)}

If any field is missing, set its value to "no value".
"""


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
async def encode_image(file: UploadFile) -> str:
    image = await file.read()
    return base64.b64encode(image).decode("utf-8")
