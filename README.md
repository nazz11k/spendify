# Spendify 💰

**Spendify** is an intelligent personal finance management platform designed to simplify expense tracking through AI automation. It combines a robust Django backend with a dedicated computer vision microservice for parsing receipts, automatic expense categorization, and providing personalized financial advice using LLMs.

## 🚀 Key Features

### 💸 Smart Expense Tracking

* **Hybrid Categorization:** Supports global standard categories alongside custom user-defined categories.
* **CRUD Operations:** Full management of income and expense transactions.
* **Analytics Dashboard:** Visual distribution of expenses by category and time (Pie/Line charts).

### 🤖 AI-Powered Receipt Scanner

A standalone microservice built on **FastAPI** that automates data entry:

* **Object Detection (YOLOv8):** Identifies key regions on a receipt (Total Amount, Date, Items).
* **OCR (PaddleOCR v4):** Extracts text with high precision from identified regions.
* **Semantic Classification (BERT/Zero-Shot):** Automatically assigns a category (e.g., "Groceries", "Health") based on the receipt context.
* **Resilience:** Implements regex fallback mechanisms to recover data even if visual detection fails.

### 🧠 AI Financial Advisor

Integrated with **Google Gemini (2.0 Flash)** to provide actionable insights:

* Analyzes monthly spending trends compared to previous periods.
* Identifies recurring unnecessary expenses.
* Generates personalized tips in English/Ukrainian to help optimize your budget.

### 🤝 Social & Bill Splitting

* **Friendship System:** Add friends and manage social connections.
* **Shared Expenses:** Effortless bill splitting without complex debt ledgers. Participants simply "leave" the shared expense when they pay their share.

## 🛠️ Tech Stack

### Backend Core

* **Framework:** Django 5, Django REST Framework (DRF)
* **Database:** PostgreSQL 15
* **Authentication:** JWT (SimpleJWT) with `dj-rest-auth`
* **Documentation:** OpenAPI 3.0 / Swagger (`drf-spectacular`)

### AI Microservice

* **Framework:** FastAPI
* **ML Models:** 
  * `Ultralytics YOLOv8` (Custom trained on receipt dataset)
  * `PaddleOCR v4` (Server & Mobile models)
  * `HuggingFace Transformers` (`cross-encoder/nli-distilroberta-base`)
* **Libraries:** PyTorch (CPU), OpenCV, NumPy

### Infrastructure

* **Containerization:** Docker, Docker Compose
* **Optimization:** Build-time model downloading to ensure offline capability and fast startup.

## 📂 Project Structure

```text
spendify/
├── backend/                 # Django Monolith (Core Logic)
│   ├── config/              # Settings & URLs
│   ├── users/               # Auth & Profiles
│   ├── transactions/        # Finance Models
│   ├── splitting/           # Social Expense Logic
│   ├── reports/             # Analytics & Aggregation
│   ├── social/              # Friends & Social
│   └── integrations/        # AI Bridges (LLM & OCR)
│
├── recipe-extraction/       # AI Microservice (FastAPI)
│   ├── app/                 # Application Code
│   └── models/              # Local Model Weights (YOLO/BERT/Paddle)
│
├── docker-compose.yml       # Orchestration
└── .env                     # Environment Variables
```
## ⚡ Getting Started

### Prerequisites

* [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

### Installation

1. **Clone the repository**

   ```bash
   git clone [https://github.com/nazz11k/spendify](https://github.com/nazz11k/spendify)
   cd spendify
   ```
Configure Environment VariablesCreate a `.env` file in the root directory. You can use the example below: 

```TOML
DEBUG=debug
SECRET_KEY=secret_key

DB_NAME=db_name
DB_USER=db_user
DB_PASSWORD=db_pass
DB_HOST=db_host
DB_PORT=db_port

RECEIPT_EXTRACTOR_API_HOST=receipt_extractor_api_host
RECEIPT_EXTRACTOR_API_PORT=receipt_extractor_api_port
RECEIPT_EXTRACTOR_API_URL=receipt_extractor_api_url

DEFAULT_LABELS=default_categories

GOOGLE_API_KEY=google_api_key

DJANGO_SUPERUSER_USERNAME=superuser_name
DJANGO_SUPERUSER_EMAIL=superuser_mail
DJANGO_SUPERUSER_PASSWORD=superuser_password
```

### Build and Run
This command will download all necessary AI models (approx. 2GB) during the build phase to ensure the containers are self-contained.
```
docker-compose up --build
```
### API Documentation
The project uses `drf-spectacular` to generate automatic documentation. Once the server is running, navigate to `/api/docs/` to see the interactive Swagger UI.

### Key Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/integrations/scan/` | Upload a receipt image for parsing and auto-creation of a transaction. |
| **GET** | `/api/integrations/advice/` | Get personalized financial advice based on recent history. |
| **GET** | `/api/reports/activity/` | Get a combined feed of personal and shared expenses. |
| **GET** | `/api/reports/by-category/` | Get aggregated spending data for visualization. |
| **POST** | `/api/splitting/spents/` | Create a shared expense with friends. |


### Running Tests
To run the test suite (pytest):

```bash
# Backend tests inside Docker container
docker-compose exec backend pytest

# Or locally (if virtualenv is active)
pytest backend/testsDocker
