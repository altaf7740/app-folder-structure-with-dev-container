FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    git \
    curl \
    sudo && \
    bash && \
    useradd -m -s /bin/bash developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir -p /home/developer/workspace && \
    chown -R developer:developer /home/developer

USER developer
WORKDIR /home/developer/workspace

CMD ["sleep", "infinity"]
