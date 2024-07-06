FROM nginx:1.24.0-alpine

COPY ./templates /etc/nginx/templates
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./cert.pem /etc/nginx/cert.pem
COPY ./key.pem /etc/nginx/key.pem
