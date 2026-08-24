# DomainArena API + demo UI
FROM python:3.12-slim
WORKDIR /app
COPY domainarena ./domainarena
COPY domainarena/web ./domainarena/web
RUN pip install --no-cache-dir fastapi uvicorn pydantic
ENV NAMECOM_MODE=production-readonly \
    PYTHONUNBUFFERED=1
EXPOSE 8801 8777
CMD ["python", "-m", "uvicorn", "domainarena.api.http:app", "--host", "0.0.0.0", "--port", "8801"]
