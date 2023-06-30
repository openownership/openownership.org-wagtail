FROM ghcr.io/hactar-is/ubuntu-20:envkey2 AS builder

# Create our working directory
RUN mkdir -p /usr/srv/app/
WORKDIR /usr/srv/app/


# Ensure docker-compose build web is able to pass these env vars in
ARG ENVKEY
ARG SERVER_ENV

####################################################################################################
# ENVKEY STUFF
####################################################################################################

ENV DOCKERFILE_VERSION=1.1

RUN eval $(envkey-source)

# Add a public / private key pair from EnvKey for connections to GitHub.
RUN mkdir -p /root/.ssh && \
    touch /root/.ssh/id_rsa && \
    touch /root/.ssh/id_rsa.pub && \
    eval $(envkey-source) && \
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

# POETRY (working and installed in django-base)
WORKDIR /usr/srv/app/
COPY ./pyproject.toml /usr/srv/app/pyproject.toml
COPY ./poetry.lock /usr/srv/app/poetry.lock
RUN mkdir -p /root/.cache/pypoetry/virtualenvs/ && \
    cd /root/.cache/pypoetry/virtualenvs/ && \
    python -m venv .venv && \
    . /root/.cache/pypoetry/virtualenvs/.venv/bin/activate && \
    cd /usr/srv/app/ && poetry install


RUN whoami
RUN ls -la

VOLUME /usr/srv/app/media

# Expose the dev server
EXPOSE 5000
