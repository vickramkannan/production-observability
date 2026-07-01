from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import time
import uuid
import logging
import json

app = FastAPI()

EMAIL = "22f3000616@ds.study.iitm.ac.in"

START_TIME = time.time()

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests"
)

logs = deque(maxlen=1000)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    HTTP_REQUESTS.inc()

    request_id = str(uuid.uuid4())

    entry = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    }

    logs.append(entry)
    logger.info(json.dumps(entry))

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
def root():
    return {"message": "Production Observability Service Running"}


@app.get("/work")
def work(n: int = 1):
    for _ in range(n):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def logs_tail(limit: int = 10):
    limit = max(1, min(limit, len(logs)))
    return list(logs)[-limit:]
