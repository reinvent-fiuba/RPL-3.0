# RPL 3.0

---

<br>
<p align="center">
  <a href="#/"><img src="https://raw.githubusercontent.com/MiguelV5/MiguelV5/main/misc/logofiubatransparent_partialwhite.png" width="60%"/></a>
</p>
<br>

---


## Table of Contents

* [General information](#general-information)
    - [Components included in this repo](#components-included-in-this-repo)
    - [How to contribute](#how-to-contribute)
* [Bootstrapping](#bootstrapping)
    - [Local within devcontainer (dev/test)](#local-within-devcontainer-docker-for-developmenttests-only)
    - [Local PROD environment via docker compose](#local-prod-environment-via-docker-compose)
    - [Local PROD environment with minikube](#local-prod-environment-with-minikube)
(WIP)

---

## General information

### Components included in this repo

This repository corresponds to the main backend services of the RPL 3.0 system. It contains the following components:
- RPL Users API
- RPL Activities API
- RabbitMQ message broker


### How to contribute

#### Coding

1. Fork the repo
2. Create a branch with the following format:
    - `feature/*`: If you are developing a new feature.
    - `bug/*`: If you are fixing a bug.
    - `chore/*`: If you are working on other kind of task.
3. When the code is ready and was properly tested, create a descriptive Pull Request, assign a reviewer and wait for some feedback.

#### Deploying

The repo has Continuous Deployment, so everything merged to `main` is deployed to prod. Please, when you merge to main, follow the GitHub action to make sure that the deployment was successful.

If you want to test a branch in prod env, you can create a `test/*` branch, this will trigger a deployment to prod. It's important to be careful while using test branches because that code will go to prod :smile:.


---


## Bootstrapping

### Local within devcontainer (Docker; For development/tests only)

Both APIs and their tests can be run within a [VSCode devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) for ease of use and reproducibility. (Requires: Docker, VSCode, Dev Containers extension)

Once inside the devcontainer:

#### Running tests

```shell
# Run all tests
python -m pytest
```

#### Running the APIs

First make sure that the MySQL container is running (the instance from `.devcontainer/metaservices.dev.yml` should start automatically). Additionally, the RabbitMQ container (from `metaservices.local.yml`) should be activated if you want to use any submission-related endpoint from the activities API here.

```shell
# to run the users API (from vscode terminal)
fastapi run rpl_users/src/main.py --reload --port 9000

# to run the activities API (from vscode terminal)
fastapi run rpl_activities/src/main.py --reload --port 9001
```
These ports are exposed so that you can access them at `localhost`



### Local PROD environment via docker compose

For integration testing and ease of use while trying patches for the whole system (compared to PROD environment via minikube), you can run the RPL 3.0 backend services locally using Docker Compose. This is the most straightforward setup for local development and testing.

#### Prerequisites and considerations

1. Ask a mantainer for a basic schema dump of the MySQL database and documentation on how to set it up for the metaservices image.
2. The `metaservices.local.yml` compose file contains multiple MySQL services since we needed them for migration purposes. You should only need the `latest` one. If you have any questions regarding the compose services feel free to ask a mantainer.
3. Both APIS require `.env` files, which should be placed within the `rpl_users` and `rpl_activities` directories, following the format of the example files. Ask a mantainer for the variables' values.
4. You can modify the `Dockerfile` files for the APIs replacing the `CMD` statement to get automatic reloads whenever you change the code (see the dockerfiles for details).

#### Running the system

- Run the metaservices compose (MySQL with the previously loaded tables from the basic schema dump, and RabbitMQ):
```shell
docker compose -f metaservices.local.yml up -d --build
```

- Run compose for the RPL Users API and RPL Activities API:
```shell
docker compose -f docker-compose.local.yml up -d --build
```

- Run compose for the RPL-Runner (see [RPL Runner repository](https://github.com/reinvent-fiuba/RPL-2.0-runner))
- Run the local setup for the frontend via `nvm` to enable automatic reload (see [RPL Frontend repository](https://github.com/reinvent-fiuba/RPL-2.0-web))

#### Accessing the APIs

You can access the APIs via:
- `http://localhost:8000` for the RPL Users API
- `http://localhost:8001` for the RPL Activities API






### Local PROD environment via minikube

For a more strict production-like environment, you can use Minikube to run the entire system. This setup is more complex and requires quite a lot of configuration and resources (also, realoading system components becomes way more tedious), but it closely resembles the production environment.

#### Prerequisites and considerations

1. Follow the prerequisites 1 and 2 from the previous section (docker compose).
2. All environment variables are set in the kubernetes files. For secrets, you must set their values individually. You can ask a mantainer for examples.

#### Running the system

- Start Minikube (and its dashboard if you want to monitor the cluster from the browser):
```shell
minikube start
minikube dashboard
```

- Start the `metaservices` compose (ONLY for the latest MySQL. Comment out the queue service since it is used directly from inside the cluster):
```shell
docker compose -f metaservices.local.yml up -d --build
```

- Start the kubernetes service and deployment for the queue:
```shell
kubectl create -f kubernetes/deployments/queue.yaml
kubectl create -f kubernetes/services/queue.yaml
```

- Build docker images for the APIs and load them into Minikube:
```shell
docker build -t rpl-users-api:local . --file rpl_users/Dockerfile
docker build -t rpl-activities-api:local . --file rpl_activities/Dockerfile
minikube image load rpl-users-api:local
minikube image load rpl-activities-api:local
```

- Start the kubernetes services and deployments for the APIs:
```shell
kubectl create -f kubernetes/deployments/rpl_users_api.yaml
kubectl create -f kubernetes/services/rpl_users_api.yaml
kubectl create -f kubernetes/deployments/rpl_activities_api.yaml
kubectl create -f kubernetes/services/rpl_activities_api.yaml
```

- You can follow the logs from the dashboard or using:
```shell
kubectl get pods
kubectl logs <pod_name> --follow
```

Now you can proceed with the instructions on both the Runner and the Frontend repositories for this particular setup.




