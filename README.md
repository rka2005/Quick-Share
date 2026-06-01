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
|   ├── api/
|   |   └── contact.js  (handle serverless connection for contact form)
|   ├── index.html
|   ├── contact.js      (handles contact form submission)
|   ├── styles.css
|   ├── vercel.json       (rewrites for backend API)
|   ├── .env            (stores environment variables for frontend)
|   └── .gitignore
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
- **Backend URL masking via Vercel rewrites**
- **Serverless contact form** powered by Vercel Functions

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
- Vanilla JavaScript
- Vercel Rewrites
- Vercel Serverless Functions

## Installation & Setup

## Serverless contact form (how it works)

- The contact form on the frontend posts to `/api/contact`.
- In production the route should be provided by a serverless platform (Vercel,
  Netlify, or similar) that maps `/api/contact` to the file
  `frontend/api/contact.js`.
- `frontend/api/contact.js` uses `nodemailer` and environment variables to send
  mail through Gmail (or any SMTP provider supported by Nodemailer).

Required environment variables for the serverless contact function:

- `GMAIL_USER` — the Gmail address to send from and receive messages to
- `GMAIL_APP_PASSWORD` — Gmail app password (recommended) or SMTP password

Note: If you prefer not to use Gmail, update the transporter configuration in
`frontend/api/contact.js` to match your SMTP provider and environment variables.

Security note: Do not commit credentials to the repo. Configure secrets in your
serverless provider dashboard (Vercel/Netlify) or use a secrets manager.


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
Serverless contact function (local emulation / dev notes):

- The `frontend/api/contact.js` file is written as an ES module serverless
  function. To test locally you can either:
  - Use a serverless framework (Vercel CLI: `vercel dev`) which will expose
    `/api/contact` and load environment variables from a `.env` file, or
  - Run a minimal Express or server that mounts that handler while setting
    `process.env.GMAIL_USER` and `process.env.GMAIL_APP_PASSWORD` locally.

Example using Vercel CLI (recommended for parity with deployment):

```bash
cd frontend
# install dependencies
npm install
# create a .env file (use .env.local for Vercel dev) with the two vars
# then run
npx vercel dev
```


## Environment Variables
| Name | Used In | Purpose |
|--------|--------|--------|
| `GMAIL_USER` | Serverless Contact API | Sender email |
| `GMAIL_APP_PASSWORD` | Serverless Contact API | SMTP authentication |


## Vercel Rewrite Configuration

Quick Share uses Vercel rewrites to proxy frontend requests to the FastAPI backend.

```json
{
  "rewrites": [
    {
      "source": "/backend/:path*",
      "destination": "https://<render-backend>/:path*"
    }
  ]
}
```

Frontend requests use:

```javascript
const API_BASE_URL = "/backend";
```

instead of exposing the backend URL directly in the client code.


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

## Deployment Architecture

```text
User
 │
 ▼
qshareio.vercel.app
 │
 ├── Frontend (HTML/CSS/JS)
 │
 ├── /api/contact
 │      ▼
 │   Vercel Serverless Function
 │
 └── /backend/*
        ▼
     Vercel Rewrite
        ▼
     FastAPI Backend (Render)
     
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

## Security Features

- Restricted CORS policy
- Temporary file expiration and cleanup
- Backend URL abstraction via Vercel rewrites
- Server-side contact form processing
- Environment-variable-based credential management

## Contact Information

- **Name:** Rohit Adak
- **Email:** rohitadak0@gmail.com
- **Phone:** +91 8348765905

## Acknowledgement

- Built with FastAPI and vanilla frontend technologies.
- Thanks to the open-source community for tools and libraries powering this project.

## License

No license file is currently included in this repository.

