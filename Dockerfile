# Use a lightweight Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install dependencies from requirements.txt
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Command to run the MCP server when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
