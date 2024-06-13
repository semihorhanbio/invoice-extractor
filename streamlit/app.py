import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import tempfile
from os import unlink


# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCT0zrmfyDXH-dxZB5PTcWjBYPut7z9gf8"
genai.configure(api_key=GEMINI_API_KEY)


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


def get_image_response(image, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([image[0], prompt])
    return response


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


model = genai.GenerativeModel(
    "gemini-1.5-pro", generation_config={"response_mime_type": "application/json"}
)

prompt = """
  You are a specialist in comprehending invoices. Input files in the form of invoices will be provided to you, and your task is to convert invoice data into json format. If the requirement information is not found, set "no value". The required properties in JSON object are as follows.
  Invoice = {"customer_name": str, "customer_vkn": int, customer_tckn": int, "vendor_name": str, "vendor_vkn": int, vendor_tckn": int, invoice_senario: str, invoice_type: str, invoice_no: str, invoice_date: date, total_of_goods_and_services: float, calculated_vat: float, invoice_total: float, invoice_lines: list[goods_and_services_name: str, goods_and_services_quantity: int, goods_and_services_unit_price: float, goods_and_services_vat_rate: float, goods_and_services_total: float]}
  Return a `Invoice`
  """

# Initialize Streamlit app
st.set_page_config("Invoice Extractor")
st.header("Invoice Extractor")
uploaded_file = st.file_uploader(
    "Choose an image or pdf", type=["jpg", "png", "jpeg", "pdf"]
)

submit = st.button("Tell me about the invoice")
if submit:
    if uploaded_file is not None:
        if uploaded_file.type.split("/")[-1] in ["jpg", "png", "jpeg"]:
            st.write("Processing Image")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            image_data = input_image_setup(uploaded_file)
            response = get_image_response(image_data, prompt)
        elif uploaded_file.type.split("/")[-1] == "pdf":
            st.write("Processing PDF")
            text = process_pdf(uploaded_file)
            st.write(text)
            response = model.generate_content([text, prompt])
        st.subheader("The Response is")
        st.write(response.text)
    else:
        st.subheader("No file uploaded")
