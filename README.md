# Short URL Generator

## Summary

This is a short URL generator built with **PostgreSQL**, **Redis**, and **FastAPI**.


The system provides a simple interface for creating and retrieving short URLs via a **REST API**.
System Overview

The system has three main components:

- **PostgreSQL shards:** Responsible for storing the generated short URLs.

- **Redis cache:** Used to improve latency by providing in-memory access.

- **FastAPI back end:** Exposes the service via a REST API.

Some quick details about each component:

#### PostgreSQL Shards

The PostgreSQL shards distribute data storage, allowing the system to **scale horizontally** in an efficient and maintainable way.


#### Redis Cache

The Redis cache **reduces latency** for memory reads thanks to its in-memory capabilities. Since the system guarantees that once a short URL is generated, it cannot be updated, **cache invalidation** is unnecessary. This simplifies the implementation and ensures high performance.


#### FastAPI

The system exposes a REST API implemented using FastAPI. With FastAPI's out-of-the-box async capabilities, all procedures are defined as **asynchronous routines**. External modules interacting with PostgreSQL and Redis are also async-capable, ensuring that the system's performance isn't limited by **network operations**.

## Requirements

To run the system, you need a [Docker](https://docker.com) installation.

## Pre-Launching

Before launching the system, you can define a few settings:

- **`NUM_DBS`**: The number of PostgreSQL shards.
- **`NUM_SHARDS`**: The number of FastAPI instances.

These values can be configured in the **`short-url/setup/.env`** file, where the system's **environment variables** are stored.

You can also specify the prefix **`(PREFIX)`** that the build phase will use for naming the created Docker images and containers. The default value is **`surl`**.

## Launching

To launch the system, navigate to the parent directory and run:

    $ make up

This will:

- **Build** the necessary Docker images.

- **Create** the corresponding Docker containers.

- **Generate** a Docker Compose file defining all the services.

- **Launch** the system using Docker Compose.

## Clean-Up

Since Docker Compose attaches **stdout** to your terminal by default, you'll first need to stop the process by pressing **`CTRL + C`**.

Then, run:

    $ make clean

This will **clean up** everything Docker-related, including the images.

## Additional Resources

**This README only covers the basics!** For more details about the system or to dive deeper into the code, check out my **Medium [list](https://medium.com/@juanfernandoplata/list/creating-a-short-url-generator-97ce8a51467d)** about the project. There, I explain my design process in depth.
