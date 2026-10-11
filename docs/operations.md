# Local operations

Readiness requires a checksum-verified complete pipeline with expected features/classes. Startup probe permits up to 120 seconds; readiness every 5 seconds; liveness every 10 seconds. API pods request 250m CPU/256Mi memory, limit 1 CPU/512Mi; inference threadpool is bounded at four concurrent slots. Two replicas on one node do not provide node fault tolerance.

Prometheus discovers pods in the assignment namespace with read-only RBAC, scrapes every five seconds, and retains up to 24 hours/256MB in ephemeral storage. The dashboard is private on localhost 8090 via a private Prometheus port-forward on 9090. Synthetic traffic can be generated with `.venv/bin/python scripts/generate_traffic.py --duration 60`.

Use explicit context `mlops-assignment`. For a failed application rollout inspect pod events, ready endpoints and JSON request logs, restore the prior recorded image tag/digest using `kubectl --context mlops-assignment -n mlops-assignment set image deployment/heart-disease-api api=PREVIOUS_IMAGE`, wait for rollout, then smoke test Ingress and confirm model version. Do not roll back to an unrelated model/schema. No failed cloud rollout or cloud high availability has been claimed.

Capture `make evidence` and export model/MLflow artifacts before stopping the cluster. Stop tunnel, dashboard, MLflow and port-forward processes when finished; `minikube stop -p mlops-assignment` releases running cluster resources without deleting data.
