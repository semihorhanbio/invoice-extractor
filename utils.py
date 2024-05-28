import fitz  # pymupdf
import re


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


def extract_values(text):
    """
    Extracts specific values from the extracted text.

    :param text: The extracted text from the PDF file.
    :return: A dictionary containing the extracted values.
    """
    values = {}

    # Extract Toplam Tutar
    match = re.search(r"Toplam Tutar\s*([\d.]+),([\d]+)", text)
    if match:
        total_amount = float(match.group(1).replace(".", "") + "." + match.group(2))
        values["Toplam Tutar"] = total_amount

    # Extract Firma Ünvanı
    match = re.search(r"Firma Ünvanı\n:(.*?)\n", text)
    if match:
        values["Firma Ünvanı"] = match.group(1).strip()

    # Extract Vergi No
    match = re.search(r"Vergi No\n:(.*?)\n", text)
    if match:
        values["Vergi No"] = match.group(1).strip()

    return values


""" def extract_image(file: UploadFile):
    img_file = io.BytesIO(await file.read())
    img = Image.open(img_file)
    text = reader.readtext(img)
    result = ""
    for detection in text:
        result += detection[1] + " "
    return result


def extract_xml(file: UploadFile):
    xml_data = await file.read()
    xml_dict = xmltodict.parse(xml_data)
    return xml_dict


def extract_excel(file: UploadFile):
    wb = openpyxl.load_workbook(await file.read())
    sheet = wb.active
    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)
    return data """
