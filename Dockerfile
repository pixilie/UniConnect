FROM python:3.12-slim

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

COPY ./app ./app
COPY ./client ./client

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
