# Apache Flink with detection engine
FROM flink:1.18.1-python3.11

WORKDIR /opt/flink/usrlib

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser || true

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV FLINK_JOB="flink_jobs/ingester_job.py" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Run Flink job
CMD ["sh", "-c", "flink run -py ${FLINK_JOB}"]
