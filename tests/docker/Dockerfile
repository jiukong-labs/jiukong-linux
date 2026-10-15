FROM debian:13 AS check-base

ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i 's/Components: main$/Components: main contrib non-free-firmware/' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o APT::Update::Error-Mode=any update \
    && apt-get install -y --no-install-recommends \
       ca-certificates python3 python3-tk shellcheck desktop-file-utils \
       libxml2-utils live-build debootstrap \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

FROM check-base AS check
COPY . /work
CMD ["bash", "tests/docker/check.sh"]
