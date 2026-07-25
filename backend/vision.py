import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """You are a beauty product identification expert.
Look at this image and identify the beauty product shown.
Return ONLY this exact format, nothing else:
BRAND: <brand name>
PRODUCT: <product name>

If you cannot confidently identify the product, return exactly:
NOT_FOUND"""

async def identify_product(image_base64: str) -> str | None:
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": PROMPT
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=100,
        )

        text = response.choices[0].message.content.strip()
        print(f"🔍 Vision response: {text}")

        if "NOT_FOUND" in text.upper():
            return None

        brand, product = "", ""
        for line in text.splitlines():
            if line.upper().startswith("BRAND:"):
                brand = line.split(":", 1)[1].strip()
            elif line.upper().startswith("PRODUCT:"):
                product = line.split(":", 1)[1].strip()

        if brand and product:
            return f"{brand} {product}"
        return None

    except Exception as e:
        print(f"Vision error: {e}")
        return None
