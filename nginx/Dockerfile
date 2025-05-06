FROM syuhas/nginx:latest


COPY index.html /usr/share/nginx/html

COPY fullchain.pem /etc/ssl/certs/fullchain.pem
COPY privkey.pem /etc/ssl/private/privkey.pem


COPY default.conf /etc/nginx/conf.d/default.conf


RUN chown 101:101 /etc/ssl/private/privkey.pem /etc/ssl/certs/fullchain.pem && \
    chmod 600 /etc/ssl/private/privkey.pem && \
    chmod 644 /etc/ssl/certs/fullchain.pem

EXPOSE 80
EXPOSE 443