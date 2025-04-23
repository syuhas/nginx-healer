# syntax=docker/dockerfile:1

FROM syuhas/pynsible:latest


WORKDIR /app

COPY . .

RUN pip3 install -e .


CMD ["runserver"]

EXPOSE 8000