# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy your FastAPI app
COPY . "${LAMBDA_TASK_ROOT}"

# Set the Lambda handler
# asgi.handler means: from asgi.py import handler
CMD ["asgi.handler"]