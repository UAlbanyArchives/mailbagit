---
layout: page
title: Docker Images
permalink: /docker/
parent: Installing mailbagit
nav_order: 3
---

# Running mailbagit in a Docker container

A docker image is available that includes all dependencies. You just need to install [Docker](https://docs.docker.com/get-docker/). Docker Desktop comes with everything you need, but you really only need Docker Engine.

Once Docker is installed, you can download the mailbagit image with the command:

```
docker pull ualbanyarchives/mailbagit
```

To run the image as a Docker container, run:

```
docker run -it ualbanyarchives/mailbagit
```

You should be able to run `mailbagit -h`, but you won't be able to do much without giving the container access to your filesystem.

## Run with access to your filesystem.

You can use a bind mount to give the container and `mailbagit` access to the files you want to process.

Mailbagit will have access to the directory listed in the `source=` argument, which will be accessible in the container using the `/data` path.

Examples:
```
docker run -it --mount type=bind,source="path/to/data",target=/data ualbanyarchives/mailbagit:dev
docker run -it --mount type=bind,source="C:\Users\Me\path\to\data",target=/data ualbanyarchives/mailbagit:dev
```

If you are using Windows, the `source=` argument should be given a Windows path with "`\`", but the container uses Unix-style paths, so it will be accessible to `mailbagit` using `/data` using "`/`".

So, if you have a PST file in `C:\Users\Me\sampleData\export.pst`, if you use
```
type=bind,source="C:\Users\Me\sampleData",target=/data
```
the PST will be accessible at `/data/export.pst`.

You could also use
```
type=bind,source="C:\Users\Me",target=/data
```
which will make the file accessible as `/data/sampleData/export.pst`

## Using Docker Desktop

Once you've downloaded the docker image with `docker pull ualbanyarchives/mailbagit`, you can also run the image using [Docker Desktop](https://www.docker.com/products/docker-desktop/).

The ualbanyarchives/mailbagit image should display. To run it, click "Run".

![Screenshot of the ualbanyarchives/mailbagit image available in Docker Desktop.]({{ site.baseurl }}/img/docker1.png)

To give the container access to your filesystem, click on the optional settings and enter a "Host Path" and an "Container Path". [This follows the same rules as described above](#run-with-access-to-your-filesystem).

![Screenshot showing how to give the container access to your filesystem.]({{ site.baseurl }}/img/docker2.png)

You can then click the "CLI" button for command line access to `mailbagit`.

![Screenshot showing how to get command line access to the container using Docker Desktop.]({{ site.baseurl }}/img/docker3.png)

Remember to stop the container when your done!

## Development Docker image

There is also a development image available:

```
docker pull ualbanyarchives/mailbagit:dev
docker run -it ualbanyarchives/mailbagit:dev
```

### Other helpful docker commands

List running containers: 
```
docker ps
```

List images:
```
docker images
```

Delete image: 
```
docker image rm <image id> -f
```
