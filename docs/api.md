# API contract

`POST /predict` accepts `tests/fixtures/valid_request.json` (synthetic). All thirteen named fields are required; `ca` and `thal` may be explicit null. Extra fields, missing keys, unknown category codes, numeric strings, Boolean substitutions, nonfinite numbers and bodies over 16 KiB are rejected. JSON integer values are accepted for continuous fields. JSON key order is irrelevant.

Response: request_id, prediction (0/1), positive_class_probability, confidence assigned to the returned prediction (`p` when 1 else `1-p`), threshold, model_version, schema_version. Scores are model estimates, not clinically calibrated risk. Invalid fields return sanitized 422 errors without values; an unavailable verified bundle returns 503; unexpected failures return a generic 500 and request ID.

/health checks process liveness; /ready checks verified model readiness; /version reports serving identity. /metrics is internal only. /docs and /openapi.json expose generated API documentation. One worker per pod avoids multiprocess metric aggregation; CPU inference executes in a threadpool.
