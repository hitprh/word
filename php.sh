#!/bin/bash


sudo apt update
sudo apt upgrade -y


sudo apt install nginx -y


sudo apt install php7.4 php7.4-fpm php7.4-curl php7.4-mysql -y

sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl start php7.4-fpm
sudo systemctl enable php7.4-fpm

sudo truncate -s 0 /etc/nginx/nginx.conf


sudo cat << 'EOF' > /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;
    gzip_disable "msie6";

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;

    send_timeout 300s;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    fastcgi_read_timeout 300s;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.php index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
    }

    location ~ /\.ht {
        deny all;
    }
}
EOF


sudo nginx -t


sudo systemctl restart nginx


echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/info.php


sudo chown www-data:www-data /var/www/html/info.php
sudo chmod 644 /var/www/html/info.php

echo "Installation and configuration complete."
