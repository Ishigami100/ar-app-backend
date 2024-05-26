

## Overview

## Techs

| Tech       | Version  |
| ---------- | -------- |
| Python     | 3.9.7    |
| Flask      | 1.1.4    |
| Kubernetes | 1.23.5   |
| Docker     | 20.10.12 |
| Nginx      | 1.21.6   |
| Mysql      | 5.7      |

## How to run with docker-compose

- You can run this application on your local with docker-compose.
- Note: Running on local cannot prepare SSL configuration, so you cannot set localhost to linebot's callback method. You can just check how this app works.

```
$ pwd
/path/to/dir/linebot/
# Build & Run containers
$ docker-compose up
# Stop & Delete containers
$ docker-compose down --rmi all --volumes --remove-orphans
```

### How to run on GKE

```

# Create your artifacts repositories on GCP.
$ gcloud artifacts repositories create ar-app-repo \
    --project= \
    --repository-format=docker \
    --location=asia-northeast1 \
    --description="Docker repository"

# Create your own cluster.
$ gcloud container clusters create ar-app-gke --num-nodes 3 --zone asia-northeast1

# Build image and deploy
$ pwd
/path/to/dir/ar-app-backend/
# Flask App image build and push
$ gcloud builds submit \
    --tag asia-northeast1-docker.pkg.dev//ar-app/app-server:1.0.0 ./app/
# Nginx container image build and push
$ gcloud builds submit \
    --tag asia-northeast1-docker.pkg.dev//ar-app/linebot-nginx:1.0.0 ./web/

# Apply each k8s objects
# Build & Run containers
kubectl apply \
    -f app/deployment.yaml \
    -f app/service.yaml \
    -f web/deployment.yaml \
    -f web/service.yaml  \
    -f db/deployment.yaml  \
    -f db/service.yaml  \
    -f db/secret.yaml  \
    -f db/configmap.yaml \
    -f db/persistent-volume.yaml \
    -f ingress/managed-cert.yaml \
    -f ingress/managed-cert-ingress.yaml
```

