import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import anyio.to_thread
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from heart_disease.api.schemas import ErrorResponse, PredictionRequest, PredictionResponse
from heart_disease.features.schema import FEATURES
from heart_disease.models.evaluate import probabilities
from heart_disease.models.package import load

logger = logging.getLogger("heart_disease.requests")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.propagate = False


def create_app(bundle=None):
    registry = CollectorRegistry()
    requests = Counter(
        "http_requests_total", "HTTP requests", ["method", "route", "status"], registry=registry
    )
    latency = Histogram(
        "http_request_duration_seconds", "Request duration", ["method", "route"], registry=registry
    )
    predictions = Counter(
        "model_predictions_total", "Predictions", ["predicted_class"], registry=registry
    )
    inference = Histogram(
        "model_inference_duration_seconds", "Inference duration", registry=registry
    )
    loaded = Gauge("model_loaded", "Verified model readiness", registry=registry)
    info = Gauge(
        "model_info",
        "Serving bundle identity",
        ["model_version", "schema_version"],
        registry=registry,
    )

    @asynccontextmanager
    async def lifespan(app):
        anyio.to_thread.current_default_thread_limiter().total_tokens = 4
        app.state.model = None
        app.state.manifest = None
        try:
            app.state.model, app.state.manifest = load(
                bundle or os.environ.get("MODEL_BUNDLE", "artifacts/model/current")
            )
            manifest = app.state.manifest
            loaded.set(1)
            info.labels(manifest["model_version"], manifest["schema_version"]).set(1)
        except Exception as exc:
            loaded.set(0)
            logger.error(
                json.dumps({"event": "model_load_failed", "error_category": type(exc).__name__})
            )
        yield
        loaded.set(0)

    app = FastAPI(
        title="Cleveland Heart Disease — Educational API", version="0.1.0", lifespan=lifespan
    )

    @app.middleware("http")
    async def request_log(request: Request, call_next):
        start = time.monotonic()
        request.state.request_id = str(uuid.uuid4())
        response = None
        try:
            # Consume at most 16 KiB, including requests with chunked bodies.
            if request.method == "POST":
                body = bytearray()
                async for chunk in request.stream():
                    if len(body) + len(chunk) > 16384:
                        response = JSONResponse(
                            {"error": "request_too_large", "request_id": request.state.request_id},
                            status_code=413,
                        )
                        break
                    body.extend(chunk)
                if response is None:
                    request._body = bytes(body)
            if response is None:
                response = await call_next(request)
        except Exception as exc:
            response = JSONResponse(
                {"error": "internal_error", "request_id": request.state.request_id}, status_code=500
            )
            logger.error(
                json.dumps(
                    {
                        "event": "request_failed",
                        "request_id": request.state.request_id,
                        "error_category": type(exc).__name__,
                    }
                )
            )
        route = getattr(request.scope.get("route"), "path", "unmatched")
        method = (
            request.method
            if request.method in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
            else "OTHER"
        )
        duration = time.monotonic() - start
        requests.labels(method, route, str(response.status_code)).inc()
        if route not in {"/health", "/ready", "/metrics"}:
            latency.labels(method, route).observe(duration)
        logger.info(
            json.dumps(
                {
                    "event": "api_request",
                    "request_id": request.state.request_id,
                    "method": method,
                    "route": route,
                    "status": response.status_code,
                    "duration_seconds": duration,
                    "model_version": (app.state.manifest or {}).get("model_version"),
                }
            )
        )
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc):
        return JSONResponse(
            {
                "error": "validation_error",
                "request_id": request.state.request_id,
                "fields": [{"field": str(e["loc"][-1]), "type": e["type"]} for e in exc.errors()],
            },
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc):
        return JSONResponse(
            {
                "error": "model_unavailable"
                if exc.status_code == 503
                else f"http_{exc.status_code}",
                "request_id": request.state.request_id,
            },
            status_code=exc.status_code,
        )

    @app.get("/health")
    def health():
        return {"status": "alive"}

    @app.get("/ready", responses={503: {"model": ErrorResponse}})
    def ready():
        if app.state.model is None:
            raise HTTPException(503, "Model unavailable")
        return {"status": "ready", "model_version": app.state.manifest["model_version"]}

    @app.get("/version", responses={503: {"model": ErrorResponse}})
    def version():
        ready()
        m = app.state.manifest
        return {key: m[key] for key in ["model_version", "schema_version", "commit", "code_hash"]}

    @app.post(
        "/predict",
        response_model=PredictionResponse,
        responses={status: {"model": ErrorResponse} for status in [413, 422, 503, 500]},
    )
    def predict(payload: PredictionRequest, request: Request):
        ready()
        frame = (
            pd.DataFrame([payload.model_dump()], columns=FEATURES)
            .astype(float)
            .replace({None: np.nan})
        )
        start = time.monotonic()
        probability = float(probabilities(app.state.model, frame)[0])
        inference.observe(time.monotonic() - start)
        m = app.state.manifest
        predicted = int(probability >= m["threshold"])
        predictions.labels(str(predicted)).inc()
        return PredictionResponse(
            request_id=request.state.request_id,
            prediction=predicted,
            positive_class_probability=probability,
            confidence=probability if predicted else 1 - probability,
            threshold=m["threshold"],
            model_version=m["model_version"],
            schema_version=m["schema_version"],
        )

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
