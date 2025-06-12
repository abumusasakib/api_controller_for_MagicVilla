# 🏡 MagicVilla API Controller (Python GUI + FastAPI)

A **GUI-based API Controller** for managing villas via a RESTful API, inspired by [DotNetMastery's MagicVilla_VillaAPI](https://github.com/bhrugen/MagicVilla_API/tree/master/MagicVilla_VillaAPI). This project demonstrates how a Python-based frontend can communicate with a FastAPI backend for complete CRUD operations using a clean, user-friendly interface.

---

## ✨ Features

- Full-featured GUI for working with villa data (create, read, update, delete)
- HTML and PDF export of villa listings
- Real-time form validation and feedback
- Logs requests with automatic log rotation
- Compatible with both the official `.NET` MagicVilla API or the included FastAPI clone (Remember to use https://)

---

## 📦 Dependencies

### Python Libraries

- `tkinter` – GUI framework
- `requests`, `json` – API interaction
- `pdfkit`, `wkhtmltopdf` – Export HTML to PDF ([Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html))
- `prettytable` – Tabular report generation
- `sqlalchemy`, `fastapi`, `uvicorn`, `pydantic[dotenv]`, `aiosqlite` – For the FastAPI backend
- `datetime`, `time`, `os`, `sys`, `logging` – Standard Python libs

---

## 🚀 How to Run

### 🖥️ Frontend (GUI)

- Make sure Python 3.9.13 is installed.
- Clone or download this repo.
- Install frontend dependencies:

```bash
   pip install prettytable requests pdfkit
```

- Run the GUI controller:

  ```bash
  python magicvilla_api_controller.py
  ```

> 🔔 **Note**: GUI talks to the API hosted at `http://localhost:7155/api/VillaAPI`.

---

### 🛠️ Backend (FastAPI Clone of MagicVilla_VillaAPI)

A FastAPI-based backend is also included as a Python clone of the original MagicVilla API.

#### API Endpoints

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| GET    | `/api/VillaAPI`      | Get all villas           |
| GET    | `/api/VillaAPI/{id}` | Get a villa by ID        |
| POST   | `/api/VillaAPI`      | Create a new villa       |
| PUT    | `/api/VillaAPI/{id}` | Fully update a villa     |
| PATCH  | `/api/VillaAPI/{id}` | Partially update a villa |
| DELETE | `/api/VillaAPI/{id}` | Delete a villa           |

#### Run the API

1. Install backend dependencies:

   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic[dotenv] aiosqlite
   ```

2. Start the server:

   ```bash
   uvicorn main:app --reload --port 7155
   ```

3. API logs will be written to:

   ```text
   logs/api_YYYY-MM-DD.log
   ```

> ✅ Logging is enabled with rotation (1 log per day, up to 7 days retained)

---

## 🐍 Python Version Management (Optional but Recommended)

Ensure you're using Python 3.9.13 for compatibility.

### 🔧 Using `pyenv` (Linux/macOS)

```bash
curl -fsSL https://pyenv.run | bash
pyenv install 3.9.13
pyenv global 3.9.13
```

### 🔧 Using `pyenv-win` (Windows)

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"
&"./install-pyenv-win.ps1"
pyenv install 3.9.13
pyenv global 3.9.13
```

---

## 📁 Project Structure

```text
.
├── main.py                      # FastAPI backend
├── magicvilla_api_controller.py# GUI controller
├── villas.db                   # SQLite database (generated)
├── villa_data.json             # Cached data from API
├── villas.html                 # Exported HTML view
├── villas.pdf                  # Exported PDF view
├── logs/
│   └── api_YYYY-MM-DD.log      # Timestamped logs with rotation
└── requirements.txt            # Python dependencies
```

---

## 👤 Author

**Abu Musa Sakib**
_This project is a Python reinterpretation of [Bhrugen Patel's](https://github.com/bhrugen) MagicVilla API, made GUI-driven and platform-agnostic._

---

## 📝 License

MIT License. Attribution encouraged.
