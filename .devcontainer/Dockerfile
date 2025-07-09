FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN apt update && \
    apt install -y --no-install-recommends sudo zsh curl git fonts-powerline && \
    curl -fsSL https://starship.rs/install.sh | sh -s -- -y && \
    useradd -m -s /bin/zsh developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /home/developer/workspace
RUN chown -R developer:developer /home/developer
COPY . .

USER developer
RUN touch ~/.zshrc


RUN uv sync
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
