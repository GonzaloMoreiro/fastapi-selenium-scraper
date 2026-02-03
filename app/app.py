from fastapi import FastAPI
from processors import run_mentions

app = FastAPI()


@app.post("/mentions")
def run(url: str):
    return run_mentions(url)