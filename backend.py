import os
import io
from PIL import Image
from google import genai
from google.genai import types
import pdf2image
from dotenv import load_dotenv
import base64

load_dotenv()

client = genai.Client()


def get_gemini_response(input, pdf_content, prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=input),
                    *pdf_content,   # already a list of Parts
                    types.Part.from_text(text=prompt)
                ]
            )
        ],
    )
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Converting pdf -> img
        images = pdf2image.convert_from_bytes(
            uploaded_file.read(),
            poppler_path=r"C:\Users\Farhan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Release-25.07.0-0\poppler-25.07.0\Library\bin"
        )

        pdf_parts = []

        # Converting into bytes
        for page in images:
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()

            pdf_parts.append(
                types.Part.from_bytes(mime_type="image/jpeg", data=img_bytes)
            )
        return pdf_parts
    else:
        raise FileNotFoundError("No File Uploaded")
