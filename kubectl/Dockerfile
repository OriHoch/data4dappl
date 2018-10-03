FROM alpine

RUN wget -qO kubectl https://storage.googleapis.com/kubernetes-release/release/$(wget -qO - https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl &&\
    chmod +x kubectl && mv ./kubectl /usr/local/bin/kubectl

RUN apk --update --no-cache add bash python grep jq python3

RUN wget -O upload_via_email_requirements.txt https://raw.githubusercontent.com/OriHoch/ckanext-upload_via_email/v0.0.5/ckanext/upload_via_email/pipelines/requirements.txt &&\
    wget -O upload_via_email_generate_ckan_config.py https://raw.githubusercontent.com/OriHoch/ckanext-upload_via_email/v0.0.5/bin/generate_ckan_config.py &&\
    pip3 install -r upload_via_email_requirements.txt

COPY kubectl.sh /
