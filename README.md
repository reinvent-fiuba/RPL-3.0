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

```shell
# Run the users API
fastapi run rpl_users/src/main.py --reload --port 9000

# Run the activities API
fastapi run rpl_activities/src/main.py --reload --port 9001
```




### Local PROD environment with minikube



(WIP)


