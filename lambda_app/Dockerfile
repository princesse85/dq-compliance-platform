FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app/ ${LAMBDA_TASK_ROOT}/app/
COPY models/ ${LAMBDA_TASK_ROOT}/models/

# Set the CMD to your handler
CMD ["app.server.handler"]
