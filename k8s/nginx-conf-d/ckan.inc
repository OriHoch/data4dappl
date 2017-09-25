location / {
    client_max_body_size 100m;
    proxy_pass http://ckan:5000/;
}
