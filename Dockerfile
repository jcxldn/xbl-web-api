FROM python:3.10.4-slim-buster

# Embed the current git commit in the runner image so that git is not required.
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

# Quicker logging, no buffer to go through first!
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY requirements.txt ./

RUN bash -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl && if [ $(dpkg --print-architecture) == "armhf" ] || [ $(dpkg --print-architecture) == "armel" ]; then DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*; fi' && sh -c "curl https://sh.rustup.rs -sSf | sh -s -- -y" && pip install -r requirements.txt

COPY . .

ENV PORT=80

EXPOSE $PORT

CMD ["python", "server.py"]