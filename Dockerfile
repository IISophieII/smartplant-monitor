FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml ./
COPY smartplant ./smartplant
RUN pip install --no-cache-dir . && useradd --create-home app && mkdir /app/data && chown app /app/data
USER app
EXPOSE 8000
CMD ["uvicorn", "smartplant.app:app", "--host", "0.0.0.0", "--port", "8000"]
