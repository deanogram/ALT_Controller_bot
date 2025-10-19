from fastapi import FastAPI

app = FastAPI(title="ALT Controller Bot API")


@app.get("/health")
def healthcheck() -> dict[str, bool]:
    return {"ok": True}
