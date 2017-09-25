location / {
    client_max_body_size 500m;
    proxy_pass http://ckan:5000/;
}
