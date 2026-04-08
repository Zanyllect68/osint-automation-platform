FROM python:3.11-slim

# instalar pdftoppm
RUN apt-get update && \
    apt-get install -y poppler-utils

# instalar flask
RUN pip install flask

WORKDIR /app
COPY server.py .

CMD ["python", "server.py"]