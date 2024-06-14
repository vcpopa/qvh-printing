FROM --platform=linux/amd64 python:3.10-slim-buster

RUN pip3 install --upgrade pip

RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    jq && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

RUN pip install --no-cache-dir \
    numpy \
    pandas \
    sqlalchemy \
    pyodbc \
    pyyaml \
    azure-keyvault-secrets \
    azure-identity \
    azure-storage-file-share \
    openpyxl \
    adal \
    requests \
    python-dotenv \
    pytest\
    pytest-cov \
    pylint\
    black \
    python-pptx \
    aiohttp \
    pydantic\
    mypy