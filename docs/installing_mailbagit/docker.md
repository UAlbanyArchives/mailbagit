---
layout: page
title: Docker Images
permalink: /docker/
parent: Installing mailbagit
nav_order: 3
---

# Running mailbagit in a Docker container

A docker image is available that includes all dependencies. You just need to install [Docker](https://docs.docker.com/get-docker/).

```
docker pull gwiedeman1/mailbag
docker run -it mailbag
```


Build with access to host filesystem. Mailbagit will have access to the directory listed in the `source=` argument.

Examples:
```
docker run -it --mount type=bind,source="path/to/data",target=/data mailbag:dev bash
docker run -it --mount type=bind,source="C:\Users\Me\path\to\data",target=/data mailbag:dev bash
```

List running containers: `docker ps`
List images: `docker images`
Delete image: `docker image rm <image id> -f`