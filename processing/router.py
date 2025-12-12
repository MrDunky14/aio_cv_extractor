import os
from processing.extractors import process_pdf, process_word
from processing.intelligence import extract_entities

def handle_upload(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    raw_text = ""
    is_image_mode = False

    try:
        # 1. Extraction
        if file_extension == '.pdf':
            raw_text = process_pdf(file_path)
            
        elif file_extension in ['.docx']:
            raw_text = process_word(file_path)
            
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            # For images, we don't extract text locally anymore.
            # We flag it so the AI knows to look at the file bytes.
            is_image_mode = True
            raw_text = "IMAGE_MODE" # Placeholder
            
        else:
            return {"error": "Unsupported File Format. Please use PDF, DOCX, or JPG/PNG."}

        if not raw_text and not is_image_mode:
            return {"error": "Failed to extract text or empty file."}

        # 2. Intelligence (AI Analysis)
        # We pass 'file_path' if it's an image, so Gemini can open it.
        extracted_data = extract_entities(raw_text, file_path=file_path if is_image_mode else None)
        
        return extracted_data

    except Exception as e:
        return {"error": f"Processing Error: {str(e)}"}