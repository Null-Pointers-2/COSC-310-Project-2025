# Best Dataset System for Movies

[![Coverage Docs](https://img.shields.io/badge/docs-coverage-blue)](https://github.com/Null-Pointers-2/COSC-310-Project-2025/tree/coverage)
[![Scrum Docs](https://img.shields.io/badge/docs-scrum-blue)](https://github.com/Null-Pointers-2/COSC-310-Project-2025/tree/scrum-documents)
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
```

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

### 4. Download the MovieLens datasets

The genome-scores.csv dataset (~400 MB) is stored as a GitHub release asset.
Download it into the correct directory:

```bash
# Linux/macOS
curl -L -o app/static/movies/genome-scores.csv \
  https://github.com/Null-Pointers-2/COSC-310-Project-2025/releases/latest/download/genome-scores.csv

# Windows PowerShell
Invoke-WebRequest -Uri "https://github.com/Null-Pointers-2/COSC-310-Project-2025/releases/latest/download/genome-scores.csv" -OutFile "app\static\movies\genome-scores.csv"
```

If the curl command doesn't work, download manually from the [Releases page](https://github.com/Null-Pointers-2/COSC-310-Project-2025/releases) and place it in `backend/app/static/movies/`.

### 5. Generate ML artifacts for recommendations

Before running the server for the first time, you need to generate the ML artifacts (feature matrices and similarity matrix) that power the recommendation system:

```bash
# From backend/ directory with venv activated:
python scripts/setup_ml_data.py
```

This process takes a few minutes and creates the following artifacts in `data/ml/`:
- `movies_clean.csv` - Preprocessed movie data
- `combined_features.npy` - Combined genre + genome feature matrix
- `similarity_matrix.npy` - Pre-computed movie similarity matrix
- `tfidf_vectorizer.pkl` - Trained TF-IDF vectorizer for genres
- `movie_id_to_idx.json` - Movie ID to matrix index mapping

**Note:** This step only needs to be run once (or when the MovieLens dataset is updated). The artifacts are gitignored because they're large (~500MB total) and derived from the source data.

### 6. Create secret key in .env

```bash
python -c "import secrets; f = open('.env', 'w', encoding='utf-8'); f.write('SECRET_KEY=' + secrets.token_urlsafe(48) + '\n'); f.close()"
```

### 7. Create .env.local in frontend/

From project root:
```bash
cd frontend
npm run setup:env
```

**Note:** Once your .env.local file is created, you will need to add your TMDB API key. More info about the API can be found [here](https://developer.themoviedb.org/docs/getting-started).

### 8. (Optional) Install pre-commit hooks for automatic linting/formatting
Once installed, pre-commit will automatically run before every git commit, to ensure code quality.

```bash
pre-commit install
```

### 9. Designating Admin Users
Admin users can be designated by modifying a user's role attribute from "user" to "admin" in backend/data/users.csv

For example, change a user from:
```
id,username,email,hashed_password,role,created_at
testuserID,testname,test@email.com,"testpassword",user,2025-11-18T16:46:43
```
To:
```
id,username,email,hashed_password,role,created_at
testuserID,testname,test@email.com,"testpassword",admin,2025-11-18T16:46:43
```

Once a user is given admin permissions, they will have access to the admin panel where they can view several system metrics, as well as the ability to administer, and resolve penalties to users.

---

## Running the Backend Server

```bash
fastapi dev app/main.py
```

Then visit:

* Interactive Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* API Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Running Tests (Pytest)

To run tests under `backend/tests/`:

```bash
# In backend/ directory with venv activated:
python -m pytest

# With coverage:
python -m pytest -v --cov=app --cov-report=html

# Run specific test types:
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only
python -m pytest tests/e2e/          # E2E tests only
```

---

## Code Linting/Formatting (Ruff)

To check code for formatting/code smells:

```bash
# In backend/ directory with venv activated:

# Check for linting issues
ruff check .

# Auto-fix what can be fixed automatically
ruff check . --fix

# Format all code
ruff format .

# Verify everything passes
ruff check .
ruff format --check .
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
