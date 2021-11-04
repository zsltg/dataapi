FROM python:3.9-slim AS base

ENV PACKAGE_NAME=dataapi
ENV MONGODB_URL=localhost
ENV MONGODB_PORT=27017

# Use a regular user instead of root
RUN groupadd --system $PACKAGE_NAME && \
    useradd --system --create-home --gid $PACKAGE_NAME $PACKAGE_NAME
USER $PACKAGE_NAME
WORKDIR /home/$PACKAGE_NAME

# Use a Python virtual environment in a Docker friendly way
ENV VIRTUAL_ENV=/home/$PACKAGE_NAME/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Install poetry
RUN python -m pip install \
    --no-cache-dir --no-warn-script-location \
    poetry

# Copy project module and dependencies
RUN mkdir /home/$PACKAGE_NAME/$PACKAGE_NAME/ 
COPY $PACKAGE_NAME/ /home/$PACKAGE_NAME/$PACKAGE_NAME/
COPY pyproject.toml poetry.lock /home/$PACKAGE_NAME/

FROM base AS release

# Install only core dependencies
RUN python -m poetry install --no-dev

# Execute package with gunicorn
ENV PORT 80
CMD exec gunicorn $PACKAGE_NAME.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4

FROM base AS test

# Copy tests
RUN mkdir /home/$PACKAGE_NAME/tests
COPY tests/ /home/$PACKAGE_NAME/tests

# Install all dependencies
RUN python -m poetry install
RUN python -m pip install tox tox-poetry-installer

# Run tests
CMD python -m pytest

FROM release