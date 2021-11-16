FROM php:7.2-apache
RUN apt-get update
RUN apt-get install -y python3

COPY matlab_check.php /var/www/html
COPY style_check.py /var/www/html
