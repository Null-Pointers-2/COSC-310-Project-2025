from fastapi import FastAPI
import uvicorn
from routers.items import router as items_router, movieRouter as movies_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items_router)
app.include_router(movies_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
