import os
import io
from PIL import Image
from google import genai
from google.genai import types
import pdf2image
import fitz
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
    if uploaded_file is None:
        raise FileNotFoundError("No File Uploaded")

    pdf_parts = []

    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        for page in doc:
            page_text = page.get_text().encode("utf-8")  # convert text to bytes

            pdf_parts.append(
                types.Part.from_bytes(
                    mime_type="text/plain",
                    data=page_text
                )
            )

        doc.close()
    except Exception as e:
        print("Error reading PDF:", e)
        raise e

    return pdf_parts
