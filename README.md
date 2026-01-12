# Quatrro Extraction Engine

A robust, production-ready document processing pipeline powered by **Gemini 2.5 Flash**. This application ingests PDF documents (mortgage frameworks, tax forms, etc.), classifies individual pages, and extracts structured data into JSON format.

## Key Features

### 🚀 VLM-Powered Extraction
- Uses **Google Gemini 2.5 Flash** (Vision-Language Model) for high-accuracy document understanding.
- **Page Classification**: Automatically identifies document types (e.g., `Form1040`, `Paystub`, `BankStatement`).
- **Data Extraction**: Extracts relevant fields (dates, amounts, names) into a standardized JSON schema.

### 🛡️ Robust Processing
- **Recitation Error Handling**: Smart fallback mechanism to handle "recitation" safety blocks by Gemini. If extraction fails due to safety filters, the system retries with a classification-only prompt to ensure no data is lost.
- **Dynamic Confidence Scoring**: Calculates confidence scores per page and aggregates them for the entire document.

### 🖥️ Modern Dashboard
- **Multiple Uploads**: Drag & drop multiple PDF files to process them in a queue.
- **3-Column Layout**:
  - **Sidebar**: Manage your file queue and upload new documents.
  - **Preview**: View the PDF file directly in the browser.
  - **Results**: See the extracted JSON data side-by-side.
- **Download**: Export the extraction results as a JSON file.

### 📊 Monitoring & Logging
- **Structured JSON Logs**: All backend logs are output as JSON for easy integration with monitoring tools (Datadog, CloudWatch, Render Logs).
- **Request Trace**: Middleware automatically logs request duration, status codes, and paths.

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI Model**: Google Gemini 2.5 Flash (`google-generativeai`)
- **PDF Processing**: PyMuPDF (`fitz`)
- **Frontend**: Vanilla JS, CSS3 (Flexbox/Grid), HTML5
- **Logging**: Python `logging` with custom JSON Formatter

## Setup

### Prerequisites
- Python 3.9+
- A Google Cloud API Key with access to Gemini models.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd quatrro
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Access the application at: `http://localhost:8000`

## Deployment

The application is optimized for deployment on platforms like **Render**, Heroku, or AWS App Runner.

- **Logging**: The app writes logs to `stdout`, which is automatically captured by most PaaS providers.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Project Structure

```
quatrro/
├── app/
│   ├── services/
│   │   └── gemini_service.py  # Core Gemini integration & logic
│   ├── static/                # Frontend assets
│   │   ├── css/
│   │   ├── js/
│   │   └── index.html
│   ├── logging_config.py      # JSON logging setup
│   ├── schemas.py             # Pydantic models
│   └── utils/
├── main.py                    # FastAPI entry & middleware
├── reproduce_issue.py         # Debugging script
├── requirements.txt
└── README.md
```
