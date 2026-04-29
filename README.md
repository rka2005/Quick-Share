<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Inter&weight=600&size=28&pause=1200&color=0EA5E9&center=true&vCenter=true&width=900&lines=Quick+Share;Share+Text+and+Files+with+Short+Codes;Fast%2C+Simple%2C+Ephemeral" alt="Typing animation" />
</p>

```text

                ██████  ██    ██ ██  ██████  ██   ██      ███████ ██   ██  █████  ██████  ███████
                ██    ██ ██    ██ ██ ██       ██  ██       ██      ██   ██ ██   ██ ██   ██ ██      
                ██    ██ ██    ██ ██ ██       █████        ███████ ███████ ███████ ██████  █████   
                ██ ▄▄ ██ ██    ██ ██ ██       ██  ██            ██ ██   ██ ██   ██ ██   ██ ██      
                ██████   ██████  ██  ██████  ██   ██      ███████ ██   ██ ██   ██ ██   ██ ███████
                    ▀▀                                                                            

```

# Quick Share

A modern, lightweight full-stack sharing app that lets users upload text snippets or files, receive a short code, and retrieve shared content instantly.

## Overview

Quick Share is built for fast, temporary content transfer. Users can:
- Share text snippets
- Upload single or multiple files
- Retrieve content with a generated code
- Preview supported content types directly in browser
- Update previously shared text by code

The backend automatically cleans up expired uploads to keep storage lean and ephemeral.

## Project Structure

```text
quick share/
├── backend/
|   ├── uploads/    (stores shared files/text)
|   ├── venv/       (created after setup)
│   ├── main.py     (backend FastAPI app)
│   ├── requirements.txt    (dependencies)
│   └── .gitignore
└── frontend/
|   ├── index.html
|   └── styles.css
└── README.md
```

## Core Features

- **Short-code sharing** for text and file content
- **Multiple file upload** support in a single share code
- **Content retrieval and preview** via code lookup
- **Text update endpoint** for editable shared snippets
- **Automatic expiration cleanup** using background scheduler
- **CORS-enabled API** for local and deployed frontend integration
- **Dark/light theme UI** with modern interactions
- **Drag-and-drop file upload** in frontend

## Tech Stack

### Backend
- Python 3.9+
- FastAPI
- Uvicorn
- APScheduler
- Pydantic
- python-multipart

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript (Fetch API)

## Installation & Setup

### 1) Clone the repository

```bash
git clone <your-repo-url>
cd "quick share"
```

### 2) Backend setup

```bash
cd backend
python -m venv .venv
```

Activate virtual environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Frontend setup

Open `frontend/index.html` with a static server (recommended):

```bash
# from project root
python -m http.server 5500 --directory frontend
```

Then open:

```text
http://localhost:5500
```

## Environment Variables

This project currently uses in-code configuration (no `.env` file required yet).

| Name | Current Value | Used In | Purpose |
|---|---|---|---|
| `UPLOAD_DIRECTORY` | `uploads` | `backend/main.py` | Storage directory for shared files/text |
| `CODE_LENGTH` | `6` | `backend/main.py` | Length of generated share code |
| `EXPIRATION_SECONDS` | `43200` (12h) | `backend/main.py` | Auto-expiration window for shared content |
| `API_BASE_URL` | `https://quick-share-xwhs.onrender.com` | `frontend/index.html` | Backend API base URL used by frontend |

If you want environment-based configuration, replace constants with `os.getenv(...)` in `backend/main.py`.

## Venv Initialization (Quick Reference)

```bash
# from backend/
python -m venv .venv
```

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# deactivate later
deactivate
```

## API Highlights

- `GET /health` — health check
- `POST /upload` — upload text or single file
- `POST /upload_multiple` — upload multiple files
- `PUT /update/{code}` — update text snippet by code
- `GET /find_file/{code}` — resolve code to content/file metadata
- `GET /view/{code}` — browser preview route
- `GET /get/{file_id}` — download single shared file
- `GET /get_multiple/{code}/{filename}` — download file from multi-upload folder

## Contact Information

- **Name:** Rohit Adak
- **Email:** rohitadak0@gmail.com
- **Phone:** +91 8348765905

## Acknowledgement

- Built with FastAPI and vanilla frontend technologies.
- Thanks to the open-source community for tools and libraries powering this project.

## License

No license file is currently included in this repository.

