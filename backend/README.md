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
git clone https://github.com/yourusername/movie-recommendations.git
cd movie-recommendations/backend
````

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # On Windows
# OR
source venv/bin/activate   # On macOS/Linux
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Server

```bash
python -m app.main
```

Then visit:

* API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests (Pytest)

To run tests under `backend/tests/`, run:

```bash
pytest -v
```

To include coverage reporting:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Docker Setup

### Build the Docker image

```bash
docker build -t movie-backend .
```

### Run the container

```bash
docker run -d -p 8000:8000 movie-backend
```

Then access the API at:
[http://localhost:8000](http://localhost:8000)

---

## License

This project is licensed under the [GPLv3](../LICENSE).

---

## Authors

*    Evan Bowness
*    Graeme Bradford
*    Patrick Rinn
*    Patrik Balazsy

---