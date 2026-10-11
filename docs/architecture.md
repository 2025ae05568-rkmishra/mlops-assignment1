# Implemented architecture

```mermaid
flowchart LR
  U[UCI pinned archive] --> C[Deterministic clean CSV]
  C --> S[Persisted train/test split]
  S --> CV[Train-only pipeline CV]
  CV --> M[MLflow comparison and selected refit]
  M --> E[Fixed held-out evaluation]
  E --> B[Checksummed full model bundle]
  B --> D[Non-root Docker API]
  D --> K[Two Minikube API pods]
  T[Traefik LoadBalancer and Ingress] --> K
  K --> P[Per-pod Prometheus scrape]
  P --> V[Private API metrics dashboard]
```

The API performs validated inference using the same fitted preprocessing/model pipeline. Requests never train models. Metrics and logs describe service behavior; no online accuracy measurement or automatic retraining is claimed. CI trains/tests/packages before container testing. Local CD is a context-scoped script. Conditional GKE remains outside the current local implementation.
