FROM python:3-slim-buster

# Embed the current git commit in the runner image so that git is not required.
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

WORKDIR /app

COPY requirements.txt ./

RUN pip install gunicorn -r requirements.txt

COPY . .

ENV PORT=80

EXPOSE $PORT

CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"]