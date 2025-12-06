# Invoice QC Service
# Invoice QC Service

A robust, automated extraction and quality control system for B2B invoices. This tool ingests PDF documents, extracts structured data using OCR/text parsing, and validates the data against strict schema and business logic rules.

**Role:** Software Engineer Intern (Data & Development) Assignment
**Stack:** Python 3.10+, FastAPI, Typer, PDFPlumber, Pydantic, Vue.js (Bonus UI)

---

## 📖 Overview

This project solves the problem of manual invoice verification. Instead of humans checking every number, this service:
1.  **Extracts** text and tables from PDF invoices (specifically formatted for German B2B standards).
2.  **Structures** the data into a standardized JSON format.
3.  **Validates** the data using math checks, date logic, and completeness rules.
4.  **Reports** results via CLI, HTTP API, or a web-based Console.

---

## 🏗 Architecture

### System Pipeline
PDF Files -> Extraction Engine (PDFPlumber) -> Raw Data -> Validation Core -> JSON Report -> CLI/API/UI

### Folder Structure
* `invoice_qc/`: Core python package.
    * `models.py`: Pydantic data schemas.
    * `extractor.py`: PDF parsing logic.
    * `validator.py`: Business logic & error accumulation.
    * `cli.py`: Typer CLI entrypoint.
    * `api.py`: FastAPI application.
* `pdfs/`: Sample input PDFs.
* `index.html`: Single-file Frontend Console.

---

## 🧠 Schema & Validation Design

### 1. Data Schema
* **Identifiers:** `invoice_number` (AUFNR), `invoice_date`.
* **Parties:** `seller_name`, `buyer_name`.
* **Financials:** `net_amount`, `tax_amount`, `gross_amount`, `currency`.
* **Line Items:** Description, quantity, unit price, total.

### 2. Validation Rules
| Rule Type | Logic | Rationale |
| :--- | :--- | :--- |
| **Completeness** | Fields must not be null. | Legal validity. |
| **Format** | Dates `YYYY-MM-DD`, Currency `EUR`. | System compatibility. |
| **Math** | `Net + Tax == Gross` (±0.05). | Financial accuracy. |
| **Math** | `Sum(Lines) == Net Total`. | Consistency check. |
| **Anomaly** | No duplicate `invoice_number`. | Prevent double payment. |

---

## 🚀 Setup & Installation

### Prerequisites
* Python 3.9+

### Installation
1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## 💻 Usage

### 1. CLI
```bash
# Extract
python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json

# Validate
python -m invoice_qc.cli validate --input-json extracted.json --report report.json

# Full Run
python -m invoice_qc.cli full-run --pdf-dir pdfs --report final_report.json
