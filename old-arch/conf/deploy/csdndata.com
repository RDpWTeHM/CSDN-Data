server {
    listen 8010;
    server_name csdndata.com;
    
    location /static {
        alias /home/joseph/var/www/csdndata.com/static;
    }
    
    location / {
        proxy_set_header Host $host;
        proxy_pass http://unix:/tmp/csdndata.com.socket;
    }
}
