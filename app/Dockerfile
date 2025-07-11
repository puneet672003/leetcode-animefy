# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI app
COPY . .

# Set the Lambda handler
# asgi.handler means: from asgi.py import handler
CMD ["asgi.handler"]
