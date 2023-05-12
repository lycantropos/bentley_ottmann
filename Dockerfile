ARG IMAGE_NAME
ARG IMAGE_VERSION

FROM ${IMAGE_NAME}:${IMAGE_VERSION}

WORKDIR /opt/bentley_ottmann

COPY pyproject.toml .
COPY README.md .
COPY setup.py .
COPY bentley_ottmann bentley_ottmann
COPY tests tests

RUN pip install -e .[tests]
