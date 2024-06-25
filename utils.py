import fitz  # pymupdf

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