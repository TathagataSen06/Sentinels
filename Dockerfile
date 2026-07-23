# syntax=docker/dockerfile:1

FROM python:3.12-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip build \
    && python -m build --wheel --outdir /dist

FROM python:3.12-slim AS runtime

# Do not buffer stdout/stderr so container logs appear immediately.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SENTINELS_CONFIG=/etc/sentinels/sentinels.yml

RUN groupadd --system sentinels \
    && useradd --system --gid sentinels --home-dir /nonexistent --shell /usr/sbin/nologin sentinels \
    && mkdir -p /var/log/sentinels /etc/sentinels \
    && chown -R sentinels:sentinels /var/log/sentinels

COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -f /tmp/*.whl

COPY config/sentinels.yml /etc/sentinels/sentinels.yml

USER sentinels
EXPOSE 9101 2222 2323 2121 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:9101/metrics', timeout=3).status==200 else 1)"

ENTRYPOINT ["sentinels"]
CMD ["run"]
