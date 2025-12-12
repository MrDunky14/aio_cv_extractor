import os
import uuid
import csv
import io
from flask import Flask, render_template, request, jsonify, make_response
from tasks import process_file_task
from processing.intelligence import calculate_match_score 


app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Async Upload: Saves file -> Starts Task -> Returns ID
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        # Generate unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # --- START BACKGROUND TASK ---
        # We don't wait for this! We just trigger it.
        task = process_file_task.delay(filepath)
        
        # Return the Task ID to the frontend
        return jsonify({"task_id": task.id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """
    Check the status of a specific background task.
    """
    task = process_file_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        return jsonify({"state": "PENDING", "status": "Processing..."})
    elif task.state == 'SUCCESS':
        return jsonify({"state": "SUCCESS", "result": task.result})
    elif task.state == 'FAILURE':
        return jsonify({"state": "FAILURE", "error": str(task.info)})
    else:
        return jsonify({"state": task.state})

import csv
import io
from flask import make_response

# ... (Keep your existing imports and routes) ...

@app.route('/download-csv', methods=['POST'])
def download_csv():
    """
    Converts the posted JSON data into a CSV file download.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data to export"}), 400

        # Create a CSV in memory (StringIO)
        si = io.StringIO()
        cw = csv.writer(si)

        # 1. Write Headers
        headers = ["File Name", "Name", "Email", "Phone", "Detected Skills", "Summary/Experience Snippet"]
        cw.writerow(headers)

        # 2. Write Rows
        for entry in data:
            # Handle potential missing keys gracefully
            file_name = entry.get('file_name', 'Unknown')
            file_data = entry.get('data', {})
            
            # Skip if error occurred in this file
            if 'error' in file_data:
                cw.writerow([file_name, "ERROR: " + str(file_data['error']), "", "", "", ""])
                continue

            meta = file_data.get('metadata', {})
            content = file_data.get('content', {})

            # Format Skills (List -> String)
            skills = ", ".join(meta.get('detected_skills', []))
            
            # Grab a snippet of text for the CSV (Summary or First Experience)
            summary_text = content.get('professional summary') or content.get('summary') or content.get('experience') or ""
            summary_snippet = summary_text[:300].replace('\n', ' ') + "..." if summary_text else ""

            cw.writerow([
                file_name,
                meta.get('name', ''),
                meta.get('email', ''),
                meta.get('phone', ''),
                skills,
                summary_snippet
            ])

        # 3. Create Response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=resumes_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
import shutil

@app.route('/reset', methods=['POST'])
def reset_session():
    """
    Clears all uploaded files and resets the session.
    """
    try:
        # Delete the entire uploads folder and recreate it
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/match-jd', methods=['POST'])
def match_jd():
    try:
        req = request.json
        resumes = req.get('resumes', [])
        jd_text = req.get('jd_text', "")
        
        if not resumes or not jd_text:
            return jsonify({"error": "Missing data"}), 400

        for resume in resumes:
            # Safely get content, defaulting to empty dict if missing
            data_block = resume.get('data', {})
            content_dict = data_block.get('content', {})
            
            # Robust flattening: Handle lists (bullets) and strings
            full_text_parts = []
            for v in content_dict.values():
                if isinstance(v, list):
                    full_text_parts.extend([str(item) for item in v])
                elif v:
                    full_text_parts.append(str(v))
            
            full_resume_text = " ".join(full_text_parts)
            
            # Calculate and inject
            score = calculate_match_score(full_resume_text, jd_text)
            
            # Ensure metadata dict exists before writing
            if 'metadata' not in data_block: data_block['metadata'] = {}
            data_block['metadata']['match_score'] = score

        return jsonify(resumes)

    except Exception as e:
        print(f"Error calculating score: {e}") # Print error to terminal for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)