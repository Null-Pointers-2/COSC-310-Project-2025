# Movie Recommendations Backend

This is the backend service for the **Best Dataset System for Movies**, built with **FastAPI**.  
It provides REST APIs for movie data, item management, and user interaction.

## Features

- FastAPI-based REST backend
- Modular architecture (repositories, routers, services, schemas)
- Async support for scalable performance
- JSON and CSV-based data sources
- Dockerized for easy deployment
- Integrated automated testing with pytest and GitHub Action

---

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
# OR
source venv/bin/activate   # On macOS/Linux
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:

* API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests (Pytest)

To run tests under `backend/tests/`, run:

```bash
# In backend/ directory with venv activated
pytest tests/ -v

# Or run specific test types
pytest tests/unit -v
pytest tests/integration -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
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

This project is licensed under the [GPLv3](../LICENSE).

---

## Authors

* Evan Bowness
* Graeme Bradford
* Patrick Rinn
* Patrik Balazsy

---