FROM python:3.11-slim

WORKDIR /app/display_app

COPY display_app/requirements.txt /app/display_app/requirements.txt
RUN pip install --no-cache-dir -r /app/display_app/requirements.txt

COPY ./display_app /app/display_app
COPY ./collector_pipeline/data /app/collector_pipeline/data

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]
