FROM ghcr.io/hactar-is/ubuntu-24:2025.1 AS builder

# Create our working directory
RUN mkdir -p /usr/srv/app/
WORKDIR /usr/srv/app/


# Ensure docker-compose build web is able to pass these env vars in
ARG SERVER_ENV
ARG GITHUB_PUBLIC_KEY
ARG GITHUB_PRIVATE_KEY
ARG PHASE_PROJECT
ARG PHASE_HOST
ARG PHASE_TOKEN

####################################################################################################
# ENVKEY STUFF
####################################################################################################

ENV DOCKERFILE_VERSION=1.1

# Add a public / private key pair from EnvKey for connections to GitHub.
RUN mkdir -p /root/.ssh && \
    touch /root/.ssh/id_rsa && \
    touch /root/.ssh/id_rsa.pub && \
    echo -e "$PRIVATE_KEY" > /root/.ssh/id_rsa && \
    echo -r "$PUBLIC_KEY" > /root/.ssh/id_rsa.pub


# Add Codebase and Github to our known hosts
RUN touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    chmod 700 /root/.ssh/id_rsa* && \
    chown -R root:root /root/.ssh

# Test SSH access (this returns false even when successful, but prints results)
RUN ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=no -vvvT git@github.com 2>&1 | grep -i auth


####################################################################################################
# PROJECT STUFF
####################################################################################################

# Not really sure what this is for. Best leave it alone.
ENV PYTHONUNBUFFERED 1

# UV (working and installed in the base images)
WORKDIR /usr/srv/app/
COPY ./pyproject.toml /usr/srv/app/pyproject.toml
COPY ./uv.lock /usr/srv/app/uv.lock
RUN . /root/uv/.venv/bin/activate && \
    cd /usr/srv/app/ && /root/.local/bin/uv sync


RUN whoami
RUN ls -la

VOLUME /usr/srv/app/media

# Expose the dev server
EXPOSE 5000
