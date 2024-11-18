FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL script
COPY etl.py etl.py

# Command to run the ETL script
CMD ["python", "etl.py"]
