ln -s /var/www/sc/config/supervisor.conf /etc/supervisor/conf.d/sc.conf

ln -s /var/www/sc/config/nginx.conf /etc/nginx/sites-enabled/sc

pip3 install -r requirements.txt