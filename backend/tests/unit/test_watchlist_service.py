from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers import watchlist

app = FastAPI()
app.include_router(watchlist.router)

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_add_to_watchlist():
    payload = {"movie_id": 1}
    response = client.post("/watchlist", json=payload)

    assert response.status_code == 401 
    # data = response.json()
    # assert data["movie_id"] == 1
    # assert data["user_id"] == "user123"

# TODO: Write more watchlist service unit tests