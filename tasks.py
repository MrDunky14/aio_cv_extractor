import os
from dotenv import load_dotenv

# Force load .env so Celery workers always have the key
load_dotenv()

from celery import Celery
from processing.router import handle_upload

# Configure Celery to use Redis
# 'app' is the name of our Flask app (which we'll link later)
redis_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

celery_app = Celery('cv_extractor', broker=redis_url, backend=redis_url)

@celery_app.task(bind=True)
def process_file_task(self, file_path):
    """
    Background Task:
    1. Receives file path.
    2. Runs the heavy extraction logic.
    3. Returns the result (stored in Redis).
    """
    try:
        # Check if file exists before processing
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        # --- RUN THE CORE LOGIC ---
        result = handle_upload(file_path)
        
        # Cleanup: Delete the temp file now that we are done
        # (We do it here, not in app.py, because app.py finishes immediately)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return result
        
    except Exception as e:
        return {"error": str(e)}