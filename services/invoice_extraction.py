import json
import re
from pydantic import ValidationError
import requests
from utils import generate_schema_string
from schemas import Invoice


def extract_invoice_data_from_image(
    image_base64: str, openai_api_key: str, img_type: str = "image/png"
):
    invoice_schema = generate_schema_string(Invoice)

    prompt = (
        "Extract the relevant data from the following invoice image into a JSON format. "
        "Do not include any additional text, explanations, or formatting. "
        "Do not use Markdown or any code fences. Only return the pure JSON object."
        "The JSON structure is defined as follows:\n"
        f"{invoice_schema}\n\n"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that extracts invoice data based on a strict schema.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{img_type};base64,{image_base64}"},
                    },
                ],
            },
        ],
        "max_tokens": 1500,
        "temperature": 0.0,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"]
        code_fence_pattern = r"^json\s*\n|```$"
        cleaned_content = re.sub(code_fence_pattern, "", raw_content)
        cleaned_content = cleaned_content.strip()
        parsed_json = json.loads(cleaned_content)
        return parsed_json
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError as json_err:
        return {
            "error": f"JSON decoding error: {str(json_err)}",
            "raw_content": raw_content if "raw_content" in locals() else None,
        }
    except ValidationError as validation_err:
        return {"error": f"Validation error: {str(validation_err)}"}


def extract_invoice_data_from_pdf(pdf_text: str, openai_api_key: str):
    """
    Extract invoice data from PDF text using the OpenAI API.

    Args:
        pdf_text (str): Extracted text from a PDF document.
        openai_api_key (str): OpenAI API key.

    Returns:
        dict: JSON response from the OpenAI API.
    """
    prompt = (
        "Extract the relevant data from the following invoice text into a JSON format. "
        "The response should contain **only** a single JSON object that strictly follows the provided schema. "
        "Do not include any additional text, explanations, or formatting.\n"
        "The JSON structure is defined as follows:\n"
        "Text from PDF:\n"
        f"{pdf_text}"
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that extracts invoice data based on a strict schema.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "invoice_schema",
                "schema": Invoice.model_json_schema(),
            },
        },
        "max_tokens": 1500,
        "temperature": 0.0,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        response_data = response.json()
        raw_content = response_data["choices"][0]["message"]["content"].strip()
        parsed_json = json.loads(raw_content)
        return parsed_json
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
