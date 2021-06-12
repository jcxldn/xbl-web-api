FROM python:3-slim-buster

# Embed the current git commit in the runner image so that git is not required.
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

# Quicker logging, no buffer to go through first!
ENV PYTHONUNBUFFERED=1
# Disable pip version checking on every command invoke
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Disable the pip cache to save on image space
ENV PIP_NO_CACHE_DIR=1

# Use a non-root account (we don't have any persistent data so don't need to worry about perms)
# useradd -l option: https://github.com/moby/moby/issues/5419#issuecomment-193876183
# Creates a system user with uid 901 inside the container
RUN groupadd -r app -g 901 && \
    useradd -l -u 901 -r -g app -m -d /home/app -s /sbin/nologin app
USER runner

WORKDIR /app

COPY requirements.txt ./

RUN pip install --user gunicorn -r requirements.txt

COPY . .

ENV PORT=80

EXPOSE $PORT

CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"]