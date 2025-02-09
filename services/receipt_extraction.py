import json
import re
import requests
from pydantic import ValidationError
from utils import generate_schema_string
from schemas import Receipt


def parse_receipt_response(raw_content: str):
    try:
        cleaned_content = re.sub(r"^json\s*\n|```$", "", raw_content).strip()
        parsed_json = json.loads(cleaned_content)
        receipt = Receipt.model_validate(parsed_json)
        return receipt.model_dump()
    except json.JSONDecodeError as json_err:
        return {
            "error": f"JSON decoding error: {str(json_err)}",
            "raw_content": raw_content,
        }
    except ValidationError as validation_err:
        return {"error": f"Validation error: {str(validation_err)}"}


def extract_receipt_data(
    image_base64: str, openai_api_key: str, img_type: str = "image/png"
):
    receipt_schema = generate_schema_string(Receipt)

    prompt = (
        "Extract the relevant data from the following receipt into a JSON format. "
        "Do not include any additional text, explanations, or formatting. "
        "Do not use Markdown or any code fences. Only return the pure JSON object. "
        "The JSON structure is defined as follows:\n"
        f"{receipt_schema}\n\n"
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
                "content": "You are an assistant that extracts receipt data based on a strict schema.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
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
        return parse_receipt_response(raw_content)

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def extract_receipt_data_from_pdf(pdf_text: str, openai_api_key: str):
    prompt = (
        "Extract the relevant data from the following receipt text into a JSON format. "
        "The response should contain **only** a single JSON object that strictly follows the provided schema. "
        "Do not include any additional text, explanations, or formatting.\n"
        "The JSON structure is defined as follows:\n"
        f"{generate_schema_string(Receipt)}\n\n"
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
                "content": "You are an assistant that extracts receipt data based on a strict schema.",
            },
            {"role": "user", "content": prompt},
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
        raw_content = response_data["choices"][0]["message"]["content"].strip()
        return parse_receipt_response(raw_content)

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
