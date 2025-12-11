ARG PROJECT_NAME=mynicegui

# These images are generated from the initializeCommand script ".devcontainer/initialize_devcontainer.sh"
FROM ${PROJECT_NAME}:base

ARG PROJECT_NAME
# USERNAME is passed from docker-compose build args and matches the local user
ARG USERNAME

USER root

# Define pre-commit cache as local -- useful for vscode and ci
ENV PRE_COMMIT_HOME=.cache/pre-commit

# Add packages needed by vscode devcontainer
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    gcc \
    g++ \
    cmake \
    make \
    iputils-ping \
    net-tools \
    tig \
    wget \
    zsh \
    build-essential \
    locales \
 && sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen \
 && locale-gen \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Set locale environment variables
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Install Terraform
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y lsb-release gnupg software-properties-common \
 && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y terraform \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y google-cloud-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Ensure the requested user exists before switching
RUN if ! id -u ${USERNAME} >/dev/null 2>&1; then useradd -ms /bin/bash ${USERNAME}; fi

USER ${USERNAME}

CMD ["sh"]

