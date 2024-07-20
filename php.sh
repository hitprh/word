#!/bin/bash

# Update and upgrade the system
sudo apt update
sudo apt upgrade -y


sudo apt install nginx -y


sudo apt install php7.4 php7.4-fpm php7.4-curl php7.4-mysql -y


sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl start php7.4-fpm
sudo systemctl enable php7.4-fpm

sudo truncate -s 0 /etc/nginx/sites-available/default


cat << 'EOF' | sudo tee /etc/nginx/sites-available/default
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


sudo sed -i '/http {/a \    # ... other configurations ...\n\n    send_timeout 300s;\n    proxy_read_timeout 300s;\n    proxy_connect_timeout 300s;\n    proxy_send_timeout 300s;\n    fastcgi_read_timeout 300s;' /etc/nginx/nginx.conf


sudo nginx -t


sudo systemctl restart nginx


echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/info.php


sudo chown www-data:www-data /var/www/html/info.php
sudo chmod 644 /var/www/html/info.php

history -c
sleep 1s
echo "Installation and configuration complete."
