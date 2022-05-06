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
docker pull ualbanyarchives/mailbag
docker run -it ualbanyarchives/mailbag
```

There is also a development image available:

```
docker pull ualbanyarchives/mailbag:dev
docker run -it ualbanyarchives/mailbag:dev
```

## Build with access to host filesystem.

You can use a bind mount to give the container and `mailbagit` access to the files you want to process.

Mailbagit will have access to the directory listed in the `source=` argument.

Examples:
```
docker run -it --mount type=bind,source="path/to/data",target=/data ualbanyarchives/mailbag:dev
docker run -it --mount type=bind,source="C:\Users\Me\path\to\data",target=/data ualbanyarchives/mailbag:dev
```

## Using Docker Desktop

Once you've pulled the docker image with `docker pull ualbanyarchives/mailbag`, you can run the image using [Docker Desktop](https://www.docker.com/products/docker-desktop/).


### Other helpful docker commands

List running containers: `docker ps`

List images: `docker images`

Delete image: `docker image rm <image id> -f`
