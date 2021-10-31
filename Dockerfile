FROM python:3-slim-buster

# Embed the current git commit in the runner image so that git is not required.
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

# Quicker logging, no buffer to go through first!
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY requirements.txt ./

RUN bash -c 'if [ $(dpkg --print-architecture) == "armv7l" ]; then apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc; fi' && pip install -r requirements.txt

COPY . .

ENV PORT=80

EXPOSE $PORT

CMD ["python", "server.py"]