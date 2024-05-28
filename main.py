from fastapi import FastAPI, File, UploadFile

from utils import extract_pdf, extract_values

app = FastAPI()

# reader = Reader(['tr'])


@app.get("/")
def health_check():
    return {
        "message": "Go to /docs route to see available routes. Send a post request /extract to extract data"
    }


@app.post("/extract/")
async def extract_data(files: list[UploadFile] = File(...)):
    extracted_data = {}
    for file in files:
        if file.content_type.startswith("application/pdf"):
            file_bytes = await file.read()
            extracted_text = extract_pdf(file_bytes)
            extracted_values = extract_values(extracted_text)
            extracted_data["data"] = extracted_values
        # elif file.content_type.startswith("image/"):
        #     extracted_data[file.filename] = extract_image(file)
        # elif file.content_type.startswith("text/xml"):
        #     extracted_data[file.filename] = extract_xml(await file.read())
        # elif file.filename.lower().endswith(".xlsx"):
        #     extracted_data[file.filename] = extract_excel(await file.read())
        else:
            extracted_data[file.filename] = (
                "Data extraction not implemented for this file type"
            )
    return extracted_data
