
---

## 4 · docker/dev.Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system deps
RUN apt-get update && apt-get install -y default-jdk git curl && \
    rm -rf /var/lib/apt/lists/*

# Spark
ENV SPARK_VERSION=3.5.1 \
    HADOOP_VERSION=3
RUN curl -sL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt
ENV SPARK_HOME=/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV PATH=$PATH:$SPARK_HOME/bin

# Python deps
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
