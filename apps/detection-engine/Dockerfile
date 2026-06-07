FROM flink:1.18.1-python3.11

WORKDIR /opt/flink/usrlib

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /opt/flink/usrlib/

ENV FLINK_JOB="flink_jobs/ingester_job.py"

CMD ["sh", "-c", "flink run -py ${FLINK_JOB}"]
