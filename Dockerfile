# ---------------- Base Layer ----------------
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# ---------------- Development Stage ----------------
FROM base AS dev

RUN apt update && \
    apt install -y --no-install-recommends sudo zsh curl git openssh-client gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt install -y nodejs

RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /opt/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions.git /opt/zsh-autosuggestions

RUN useradd -m -s /bin/zsh developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

USER developer
WORKDIR /home/developer/workspace

# use "catppuccin-powerline" with "pure-preset" of starship if you don't have nerd-fonts installed in your host OS.
# If set then also check for vscode terminal fonts, it should be either 'MesloLGS Nerd Font Mono' or 'Fira Code'
RUN mkdir -p ~/.config && \
    starship preset catppuccin-powerline --output ~/.config/starship.toml && \  
    echo 'export STARSHIP_CONFIG="$HOME/.config/starship.toml"' >> ~/.zshrc && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    echo 'source /opt/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> ~/.zshrc && \
    echo 'source /opt/zsh-autosuggestions/zsh-autosuggestions.zsh' >> ~/.zshrc && \
    echo 'ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#999999"' >> ~/.zshrc

COPY --chown=developer:developer . .

RUN uv sync --dev

EXPOSE 8000 5173
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ---------------- Production Stage ----------------
FROM base AS prod

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1001 appuser

WORKDIR /home/appuser/app

COPY pyproject.toml poetry.lock* ./

RUN uv sync --no-dev --no-install

COPY . .

RUN chown -R appuser:appuser /home/appuser

RUN uv pip install . --target /opt/app

USER appuser
WORKDIR /opt/app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
