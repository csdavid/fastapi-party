###########
# BUILDER #
###########

FROM python:3.13-slim-bookworm AS builder

# install system dependencies
RUN apt-get update \
    && apt-get -y install g++ ca-certificates curl gnupg \
    && apt-get clean

# install node
ENV NODE_MAJOR=22
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install nodejs -y

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install python dependencies
COPY . .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# Install Node.js dependencies
COPY package.json package-lock.json ./
RUN npm install

# Build Tailwind
RUN pip install -r requirements.txt && npm run tailwind:build

#########
# FINAL #
#########

# pull official base image
FROM python:3.13-slim-bookworm

# upgrade system packages
RUN apt-get update && apt-get upgrade -y && apt-get clean

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=prod
ENV TESTING=0
ENV PYTHONPATH=$APP_HOME

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME
COPY --from=builder /usr/src/app/party_app/static/css/output.css /home/app/web/party_app/static/css/output.css

# chown all the files to the app user
RUN chown -R app:app $HOME
# change to the app user
USER app
# serve the application
CMD exec uvicorn party_app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"
#CMD ["uvicorn", "party_app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}", "--proxy-headers", "--forwarded-allow-ips=*"]