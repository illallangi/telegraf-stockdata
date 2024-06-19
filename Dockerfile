# Main image
FROM docker.io/library/debian:bookworm-20240612
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install packages
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && \
  apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    ca-certificates=20230311 \
    curl=7.88.1-10+deb12u5 \
    gnupg=2.2.40-1.1 \
    gnupg1=1.4.23-1.1+b1 \
    gnupg2=2.2.40-1.1 \
    libpq-dev=15.6-0+deb12u1 \
    lm-sensors=1:3.6.0-7.1 \
    musl=1.2.3-1 \
    postgresql-common=248 \
    python3-dev=3.11.2-1+b1 \
    python3-pip=23.0.1+dfsg-1 \
    python3-setuptools=66.1.1-1 \
    snmp=5.9.3+dfsg-2 \
    xz-utils=5.4.1-0.2 \
  && \
  apt-get clean \
  && \
  rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    XDG_CONFIG_HOME=/config \
    TELEGRAF_INTERVAL=1200 \
    INFLUXDB_DATABASE=stockdata

# FIXME: hadolint ignore
# hadolint ignore=SC2002
RUN DEBIAN_FRONTEND=noninteractive \
  curl -s https://repos.influxdata.com/influxdata-archive_compat.key > influxdata-archive_compat.key \ 
  && \
  echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor > /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg \
  && \
  echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' > /etc/apt/sources.list.d/influxdata.list \
  && \
  rm -f influxdata-archive_compat.key \
  && \
  apt-get update \
  && \
  apt-get install -y --no-install-recommends \
    telegraf=1.25.2-1 \
  && \
  apt-get clean \
  && \
  rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY rootfs/usr/src/app/requirements.txt /usr/src/app/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /usr/src/app/requirements.txt

# add local files
COPY rootfs/ /

# set entrypoint and command
ENTRYPOINT ["custom-entrypoint"]
CMD ["/usr/bin/telegraf"]
