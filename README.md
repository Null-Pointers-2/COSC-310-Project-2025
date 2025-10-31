# Best Dataset System for Movies

[![Coverage Docs](https://img.shields.io/badge/docs-coverage-blue)](https://github.com/Null-Pointers-2/COSC-310-Project-2025/tree/coverage)
[![Build Status](https://github.com/Null-Pointers-2/COSC-310-Project-2025/actions/workflows/ci.yml/badge.svg)](https://github.com/Null-Pointers-2/COSC-310-Project-2025/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPLv3-blue)](https://www.gnu.org/licenses/gpl-3.0.en.html)

A Software Engineering Project for COSC 310 (2025)

## Team Members

- Evan Bowness
- Graeme Bradford
- Patrick Rinn
- Patrik Balazsy

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Null-Pointers-2/COSC-310-Project-2025.git
cd COSC-310-Project-2025/backend
````

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate.bat  # On Windows
source venv/bin/activate   # On macOS/Linux
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Create secret key in .env

```bash
python -c "import secrets; f = open('.env', 'w', encoding='utf-8'); f.write('SECRET_KEY=' + secrets.token_urlsafe(48) + '\n'); f.close()"
```

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:

* Interactive Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* API Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests (Pytest)

To run tests under `backend/tests/`, run:

```bash
# In backend/ directory with venv activated:
python -m pytest

# With coverage:
python -m pytest -v --cov=app --cov-report=html
```

---

## Docker Setup

### Build the Docker image

```bash
# From project root:
docker compose build
```

### Run the container

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Or view specific service logs
docker compose logs -f backend
docker compose logs -f frontend
```

Then access the API at:
[http://localhost:8000](http://localhost:8000/health)

Or the frontend at:
[http://localhost:3000](http://localhost:3000)

---

## License
This project is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html).
