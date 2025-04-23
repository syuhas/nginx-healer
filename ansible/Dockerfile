# syntax=docker/dockerfile:1

FROM syuhas/pynsible:latest


WORKDIR /app

COPY . .

RUN chmod 600 /app/config/ec2.pem

RUN pip3 install -e .


CMD ["runserver"]

EXPOSE 8000