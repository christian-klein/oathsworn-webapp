# Stage 1: Build Java JRE
FROM eclipse-temurin:17-jre AS java

# Stage 2: Data Extraction & Web Asset Builder
FROM python:3.12-slim AS builder

# Copy Java JRE from Java stage
COPY --from=java /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install utilities needed to download jadx and transcode audio/images
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        unzip \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Download and install jadx
ARG JADX_VERSION=1.5.5
ARG JADX_SHA256=38a5766d3c8170c41566b4b13ea0ede2430e3008421af4927235c2880234d51a

RUN wget -q "https://github.com/skylot/jadx/releases/download/v${JADX_VERSION}/jadx-${JADX_VERSION}.zip" \
    && echo "${JADX_SHA256}  jadx-${JADX_VERSION}.zip" | sha256sum -c - \
    && unzip "jadx-${JADX_VERSION}.zip" -d /opt/jadx \
    && rm "jadx-${JADX_VERSION}.zip" \
    && chmod +x /opt/jadx/bin/jadx

ENV PATH="/opt/jadx/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV APK_CACHE_DIR=/cache

ARG INCLUDE_GERMAN_LANG=""
ENV INCLUDE_GERMAN_LANG=${INCLUDE_GERMAN_LANG}

WORKDIR /repo

RUN pip install --no-cache-dir gdown Pillow

# Copy cache (if local APK exists) and repository files
COPY cache/ /cache/
COPY web/ web/
COPY scripts/ scripts/

# Run setup to decompile APK and generate compressed web data
RUN python3 scripts/setup.py

# Stage 3: Production Caddy Web Server + Backup Daemon
FROM caddy:2-alpine AS runtime

RUN apk add --no-cache python3

# Copy web files (including generated data) into Caddy document root
COPY --from=builder /repo/web /srv

# Copy Caddy configuration and backup scripts
COPY serve/Caddyfile /etc/caddy/Caddyfile
COPY scripts/backup_server.py /opt/backup_server.py
COPY scripts/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && mkdir -p /backups

EXPOSE 8080

CMD ["/entrypoint.sh"]
