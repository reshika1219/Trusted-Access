from fastapi import FastAPI

app = FastAPI(
    title="Trusted Access",
    description=(
        "Privacy-first prototype for controlled emergency information sharing. "
        "This service is not production-secure or legally certified."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
