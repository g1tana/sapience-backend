import pytesseract
from PIL import Image
from fastapi import UploadFile
from memory import store_memory
import os
import io

# Ensure Tesseract is found
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ingest_image(file: UploadFile, meta: dict = {}, force_local: bool = False) -> dict:
    try:
        # Load image from upload
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Run OCR
        extracted_text = pytesseract.image_to_string(image)
        if not extracted_text.strip():
            return { "status": "empty", "text": "", "message": "No readable text found in image." }

        # Store in memory
        store_memory(extracted_text, {
            **meta,
            "modality": "image",
            "filename": file.filename
        }, force_local=force_local)

        return {
            "status": "success",
            "text": extracted_text,
            "message": "Text extracted and stored successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "text": "",
            "message": f"OCR failed: {str(e)}"
        }