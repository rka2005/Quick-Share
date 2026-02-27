import os
import string
import random
import html
import time
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Initialize the app only ONCE.
app = FastAPI()

# Updated origins list as requested.
# This tells the browser which frontend URLs are allowed to make requests to this backend.
origins = [
    "http://localhost:5500",          # For local testing
    "http://127.0.0.1:5500",         # For local testing
    "https://quick-share-xwhs.onrender.com", # Added as requested
    "*"                               # Wildcard for easy development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIRECTORY = "uploads"
CODE_LENGTH = 6
EXPIRATION_SECONDS = 12 * 60 * 60  # 12 hours

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# This was the duplicate app = FastAPI() line that has been removed.

class TextItem(BaseModel):
    content: str

# ✨ --- START: BACKGROUND CLEANUP LOGIC --- ✨

def cleanup_old_files():
    """Scans the upload directory and deletes files older than 24 hours."""
    print("Running scheduled cleanup of old files...")
    current_time = time.time()
    for filename in os.listdir(UPLOAD_DIRECTORY):
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        try:
            # Use modification time, so updating a text resets its timer
            file_mod_time = os.path.getmtime(file_path)
            if (current_time - file_mod_time) > EXPIRATION_SECONDS:
                os.remove(file_path)
                print(f"Deleted expired file: {filename}")
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error cleaning up file {filename}: {e}")

@app.get("/health")
async def health():
    return {"status": "alive"}

@app.on_event("startup")
async def startup_event():
    """Initializes and starts the background scheduler on server startup."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_old_files, 'interval', hours=1)
    scheduler.start()
    print("Background scheduler for file cleanup has been started.")

# ✨ ---  END: BACKGROUND CLEANUP LOGIC  --- ✨

def generate_unique_code():
    """Generates a unique uppercase alphabetic code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=CODE_LENGTH))
        found = False
        for filename in os.listdir(UPLOAD_DIRECTORY):
            if filename.startswith(code):
                found = True
                break
        if not found:
            return code

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    # This assumes an index.html file exists in the same directory.
    # On Render, you may need to ensure this file is present.
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Welcome to Quick Share</h1><p>index.html not found.</p>", status_code=404)


@app.post("/upload")
async def create_upload(text_content: str = Form(None), file: UploadFile = File(None)):
    """Handle upload and generate a short code."""
    if not text_content and (not file or not file.filename):
        raise HTTPException(status_code=400, detail="No text or file provided.")

    code = generate_unique_code()

    if file and file.filename:
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{code}{file_extension}")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return {"message": "File uploaded successfully!", "code": code}

    if text_content:
        normalized_content = text_content.replace('\r\n', '\n').replace('\r', '\n')
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{code}.txt")
        with open(file_path, "w", encoding="utf-8") as buffer:
            buffer.write(normalized_content)
        return {"message": "Text shared successfully!", "code": code}

    raise HTTPException(status_code=400, detail="Invalid request.")

@app.post("/upload_multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    """
    Handles uploading multiple files.
    Each batch of uploads is stored in a unique folder named after the generated code.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    code = generate_unique_code()
    folder_path = os.path.join(UPLOAD_DIRECTORY, code)
    os.makedirs(folder_path, exist_ok=True)

    saved_files = []

    for i, file in enumerate(files, start=1):
        if not file.filename:
            continue  # skip empty inputs

        file_extension = os.path.splitext(file.filename)[1]
        safe_name = os.path.basename(file.filename)
        file_path = os.path.join(folder_path, safe_name)

        # Save each file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        saved_files.append(safe_name)

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid files uploaded.")

    return {
        "message": "Files uploaded successfully!",
        "code": code,
        "files": saved_files
    }


@app.put("/update/{code}")
async def update_text(code: str, item: TextItem):
    """Finds a text file by its code and updates its content."""
    code = code.upper()
    filename = f"{code}.txt"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Code not found or is not a text snippet.")

    normalized_content = item.content.replace('\r\n', '\n').replace('\r', '\n')

    with open(file_path, "w", encoding="utf-8") as buffer:
        buffer.write(normalized_content)

    return {"message": "Text updated successfully!"}


@app.get("/find_file/{code}")
async def find_file_by_code(code: str):
    """
    Finds a single file or a folder by code. 
    If it's a folder, returns list of files.
    """
    code = code.upper()
    folder_path = os.path.join(UPLOAD_DIRECTORY, code)

    # --- Multiple files case ---
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
        if not files:
            raise HTTPException(status_code=404, detail="No files found for this code.")
        return {"type": "multiple", "files": files, "folder": code}

    # --- Single file case ---
    found_filename = None
    for filename in os.listdir(UPLOAD_DIRECTORY):
        if filename.startswith(code):
            found_filename = filename
            break

    if not found_filename:
        raise HTTPException(status_code=404, detail="Code not found.")

    file_path = os.path.join(UPLOAD_DIRECTORY, found_filename)

    if found_filename.endswith(".txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"type": "text", "content": content, "filename": found_filename}
        except Exception:
            pass

    return {"type": "file", "filename": found_filename}

@app.get("/view/{code}", response_class=HTMLResponse)
async def view_shared_content(code: str):
    code = code.upper()
    folder_path = os.path.join(UPLOAD_DIRECTORY, code)

    # ✅ Multiple file case
    if os.path.isdir(folder_path):
        files = os.listdir(folder_path)
        if not files:
            raise HTTPException(status_code=404, detail="No files in folder.")

        # --- Preview different file types ---
        def is_text(f): return any(f.endswith(ext) for ext in [".txt", ".py", ".js", ".html", ".css", ".json", ".md"])
        def is_image(f): return any(f.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"])
        def is_pdf(f): return f.endswith(".pdf")

        previews = ""
        for f in files:
            file_url = f"/get_multiple/{code}/{f}"
            safe_name = html.escape(f)

            if is_text(f):
                with open(os.path.join(folder_path, f), "r", encoding="utf-8", errors="ignore") as file_data:
                    content = html.escape(file_data.read()[:5000])  # limit preview size
                previews += f"<h3>📄 {safe_name}</h3><pre style='background:#f8f9fa;padding:10px;border-radius:8px;'>{content}</pre><hr>"
            elif is_image(f):
                previews += f"<h3>🖼️ {safe_name}</h3><img src='{file_url}' alt='{safe_name}' style='max-width:100%;border-radius:10px;'/><hr>"
            elif is_pdf(f):
                previews += f"<h3>📘 {safe_name}</h3><embed src='{file_url}' type='application/pdf' width='100%' height='500px'/><hr>"
            else:
                previews += f"<h3>📦 {safe_name}</h3><a href='{file_url}' target='_blank'>Download</a><hr>"

        html_content = f"""
        <html>
        <head><title>Quick Share - {code}</title></head>
        <body style="font-family:Arial;margin:30px;">
            <h2>📂 Files for code: {code}</h2>
            {previews}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    # ✅ Single file or text case
    found_filename = None
    for filename in os.listdir(UPLOAD_DIRECTORY):
        if filename.startswith(code):
            found_filename = filename
            break

    if not found_filename:
        raise HTTPException(status_code=404, detail="Code not found.")

    file_path = os.path.join(UPLOAD_DIRECTORY, found_filename)

    # Display text file content
    if found_filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = html.escape(f.read())
        return HTMLResponse(f"<pre>{content}</pre>")

    # Other files: download link
    return HTMLResponse(f"<a href='/get/{found_filename}'>Download {found_filename}</a>")


@app.get("/get/{file_id}")
async def get_shared_content(file_id: str):
    """Serve the shared file for downloading."""
    file_path = os.path.join(UPLOAD_DIRECTORY, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Content not found.")
    return FileResponse(path=file_path)

@app.get("/get_multiple/{code}/{filename}")
async def get_file_from_folder(code: str, filename: str):
    folder_path = os.path.join(UPLOAD_DIRECTORY, code)
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path=file_path, filename=filename)