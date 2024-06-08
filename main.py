from fastapi import FastAPI, File, UploadFile
from PIL import Image
import PyPDF2
import tempfile
from os import unlink
import google.generativeai as genai

app = FastAPI()

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCT0zrmfyDXH-dxZB5PTcWjBYPut7z9gf8"
genai.configure(api_key=GEMINI_API_KEY)


@app.post("/extract/")
async def extract_data(files: list[UploadFile] = File(...)):
    extracted_data = {}
    model = genai.GenerativeModel(
        "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
    )

    prompt = """
  You are a specialist in comprehending invoices. Input files in the form of invoices will be provided to you, and your task is to convert invoice data into json format. If the requirement information is not found, set "no value". The required properties in JSON object are as follows.
  Invoice = {"invoice_total": str, "customer_name": str, "customer_vkn": str, invoice_date: date}
  Return a `Invoice`
  """
    for file in files:
        if file.content_type.startswith("application/pdf"):
            file_bytes = await file.read()
            extracted_text = process_pdf(file_bytes)
            gemini_response = model.generate_content([extracted_text, prompt])
            extracted_data["data"] = gemini_response.text
        elif file.content_type.startswith("image/"):
            image_parts = input_image_setup(file)
            gemini_response = get_image_response(image_parts, prompt)
            extracted_data["data"] = gemini_response.text
        else:
            extracted_data[file.filename] = (
                "Data extraction not implemented for this file type"
            )
    return extracted_data


def process_pdf(uploaded_file):
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()

            with open(temp_file.name, "rb") as pdf_file_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page_obj = pdf_reader.pages[page_num]
                    text += page_obj.extract_text()

        # Delete the temporary file
        unlink(temp_file.name)

        return text

    return ""


def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data,
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


def get_image_response(image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([image[0], prompt])
    return response
