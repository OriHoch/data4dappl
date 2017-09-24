#!/usr/bin/env python
import yaml, sys

if len(sys.argv) != 3:
    print("usage: bin/k8s_update_deployment_image.py <k8s_deployment_name> <image_url>")
    exit(1)
else:
    deployment = sys.argv[1]
    image = sys.argv[2]

    if deployment not in ["ckan"]:
        raise Exception("Unsupported deployment: {}".format(deployment))

    with open("k8s/{}.yaml".format(deployment)) as f:
        docs = list(yaml.load_all(f))

    docs[2]["spec"]["template"]["spec"]["containers"][0]["image"] = image

    with open("k8s/{}.yaml".format(deployment), "w") as f:
        yaml.dump_all(docs, f)

    exit(0)
