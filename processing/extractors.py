import pdfplumber
import docx
from PIL import Image
import io

def process_pdf(file_path):
    """
    Extracts text from PDF using pdfplumber.
    Fast and pure Python.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # layout=True helps preserve physical column layout
                page_text = page.extract_text(layout=True)
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text

def process_word(file_path):
    """
    Extracts text from .docx files.
    DROPPED SUPPORT: Old binary .doc files (pre-2007).
    Reason: Requires 'antiword' binary and 'textract' (deprecated).
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n\n"
    except Exception as e:
        print(f"Error reading Word Doc: {e}")
        return ""
    return text

def process_image(file_path):
    """
    Legacy OCR removal:
    Instead of using Tesseract here, we just validate the image.
    We will pass the Image object DIRECTLY to Gemini in intelligence.py.
    """
    try:
        # Just ensure it's a valid image file
        with Image.open(file_path) as img:
            img.verify() 
        
        # Return a flag indicating this is an image, handled downstream
        return "IMAGE_FILE_DETECTED", False
    except Exception as e:
        return f"Error reading Image: {e}", True