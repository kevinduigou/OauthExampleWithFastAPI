ARG PROJECT_NAME=mynicegui
ARG USERNAME=vscode

FROM mcr.microsoft.com/devcontainers/python:3.13

ARG PROJECT_NAME
ARG USERNAME

# Prepare workspace directory
WORKDIR /workspaces/${PROJECT_NAME}

# Ensure the configured user exists for downstream layers
RUN if ! id -u ${USERNAME} >/dev/null 2>&1; then useradd -ms /bin/bash ${USERNAME}; fi

USER ${USERNAME}

