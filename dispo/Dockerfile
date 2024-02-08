FROM python:3.12 as base

WORKDIR /svc

RUN pip install poetry && \
  python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | \
  /venv/bin/pip install -r /dev/stdin


FROM python:3.12

WORKDIR /svc

COPY --from=base /venv /venv
COPY . .
RUN chmod u+x *.sh

EXPOSE 8000

CMD ["./start.sh"]
