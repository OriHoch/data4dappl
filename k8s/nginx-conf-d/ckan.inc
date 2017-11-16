# location /fantastic/ {
#     proxy_cache nginx_ckan;
#     proxy_pass http://ckan:5000;
# }

# location /base/images/ {
#     proxy_cache nginx_ckan;
#     proxy_pass http://ckan:5000;
# }

# location /odata-logo.png {
#     proxy_cache nginx_ckan;
#     proxy_pass http://ckan:5000;
# }

location / {
    client_max_body_size 500m;
    proxy_pass http://ckan:5000/;
}
