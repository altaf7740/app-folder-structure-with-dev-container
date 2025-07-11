FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN apt update && \
    apt install -y --no-install-recommends sudo zsh curl git openssh-client && \
    curl -fsSL https://starship.rs/install.sh | sh -s -- -y && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /opt/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions.git /opt/zsh-autosuggestions && \
    useradd -m -s /bin/zsh developer && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /home/developer/workspace
RUN chown -R developer:developer /home/developer
COPY . .

USER developer

RUN mkdir -p ~/.config && \
    starship preset pure-preset --output $HOME/.config/starship.toml && \
    echo 'export STARSHIP_CONFIG="$HOME/.config/starship.toml"' >> ~/.zshrc && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    echo 'source /opt/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> ~/.zshrc && \
    echo 'source /opt/zsh-autosuggestions/zsh-autosuggestions.zsh' >> ~/.zshrc && \
    echo 'ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#999999"' >> ~/.zshrc


RUN uv sync
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
