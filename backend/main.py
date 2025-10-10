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
    Finds a file by code, determines its type, and returns its content if it's text.
    """
    code = code.upper()
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
    """Finds content by code and displays it on a viewer page."""
    code = code.upper()
    found_filename = None
    for filename in os.listdir(UPLOAD_DIRECTORY):
        if filename.startswith(code):
            found_filename = filename
            break

    if not found_filename:
        raise HTTPException(status_code=404, detail="Code not found.")

    file_path = os.path.join(UPLOAD_DIRECTORY, found_filename)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    escaped_content = html.escape(content)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Viewer</title>
        <style>
            body {{ font-family: sans-serif; background-color: #f4f7f6; margin: 0; }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                background-color: #2b2b2b;
                color: #f8f8f2;
                padding: 25px;
                border-radius: 8px;
                margin: 20px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
            }}
        </style>
    </head>
    <body><pre>{escaped_content}</pre></body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/get/{file_id}")
async def get_shared_content(file_id: str):
    """Serve the shared file for downloading."""
    file_path = os.path.join(UPLOAD_DIRECTORY, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Content not found.")
    return FileResponse(path=file_path)