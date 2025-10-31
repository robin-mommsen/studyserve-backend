FROM alpine:3.22.1

ENV PYTHON_VERSION=3.13.4

# Install system dependencies
RUN apk add --no-cache \
    wget \
    curl \
    gnupg \
    build-base \
    gcc \
    musl-dev \
    zlib-dev \
    ncurses-dev \
    gdbm-dev \
    nss-dev \
    openssl-dev \
    openssh \
    readline-dev \
    libffi-dev \
    sqlite-dev \
    bzip2-dev \
    ca-certificates \
    python3-dev \
    libpq-dev \
    ansible \
    sshpass \
    jq \
    bash \
    python3 \
    py3-pip \
    linux-headers \
    lsb-release \
    coreutils

# Symlink für python → python3 (optional)
RUN ln -sf python3 /usr/bin/python && ln -sf pip3 /usr/bin/pip



# Install Terraform
RUN wget https://releases.hashicorp.com/terraform/1.12.2/terraform_1.12.2_linux_amd64.zip && \
    unzip terraform_1.12.2_linux_amd64.zip -d /usr/local/bin && \
    rm terraform_1.12.2_linux_amd64.zip

# Set working directory
WORKDIR /app
COPY . .

# Venv anlegen
RUN python3 -m venv /opt/venv

# Venv aktivieren & Pfad global setzen
ENV PATH="/opt/venv/bin:$PATH"

# Installiere Python-Abhängigkeiten im venv
RUN chmod +x /app/entrypoint.sh && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

WORKDIR /app/server

RUN test -f manage.py

ENV DJANGO_SETTINGS_MODULE=config.settings
ENV DEBUG=False

EXPOSE 8000

COPY docker-entrypoint-tf.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint-tf.sh && \
    chmod +x /usr/local/bin/docker-entrypoint-tf.sh

ENTRYPOINT ["docker-entrypoint-tf.sh"]
