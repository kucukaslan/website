---
title: "Notes on Uvicorn on Production"
date: 2025-10-29T20:25:10+03:00
tags: ['english', 'python', 'uvicorn', 'fastapi', 'production']
draft: false
---

The Uvicorn + FastAPI is a common default stack for Python web applications.

However, it is just too easy to use it with a wrong configuration on the production environment.

A naive person would install the FastAPI and uvicorn using the `pip install FastAPI uvicorn` (or `uv add FastAPI uvicorn`) command.

This is not incorrect, it will work, but it leaves low-hanging fruits untouched.

## uvloop and httptools
However, when uvicorn is installed this way, it uses `asyncio`'s default event loop for corresponding platform, which is usually a pure Python implementation.

Remember the rule of thumb for Python is **avoid a pure Python implementation of anything**,
not even the freaking `for` loops are an exception (use numpy, pandas, etc. where possible).

So, we can't, in our right mind, use that pure Python event loop.
Luckily, there is a commonly suggested non-Python event loop implementation: `uvloop`.
It is included in the uvicorn's standard dependencies, so we can just install it using the `uv add 'uvloop[standard]'` command.

Similarly, by default uvicorn uses a pure Python http parser. Again, there is a non-Python http parser implementation: `httptools` which is also included in the uvicorn[standard] dependencies.

## Don't Use Gunicorn on Kubernetes, Don't Use Multiple Workers
The natural next step following the prototyping the Python server is to Dockerize it to be deployed in the production environment possibly on a Kubernetes cluster.

Now, that you've seen the naive mistake in installing uvicorn, you might want to be smart before you prepare production configuration and done some research.

You possibly asked some famous LLMs or even found [uvicorn.dev/deployment](https://uvicorn.dev/deployment/) and actually read the documentation by yourself like the old people.

Right there, in the official documentation, you see the following advice:
> Run `gunicorn -k uvicorn.workers.UvicornWorker` for production.

or see
> gunicorn -w 4 -k uvicorn.workers.UvicornWorker


below. Don't do it.
Not because it's wrong.
In fact this suggestion is great -but for the old-school reliable deployments to dedicated servers.

Gunicorn is yet another layer on top of the server.
It's used to manage multiple copies of the server in the same machine: distributing the load among them, restart them if they crash, etc.

When you deploy your application to a Kubernetes cluster, you already have a layer of load balancing and scaling. If you need multiple copies of the server, you should use multiple Kubernetes Pods. Kubernetes can manage it as well as Gunicorn can. Also, with Kubernetes you get to deploy them on different nodes, and deploy other services on the same nodes.

If Gunicorn is used with Kubernetes, then it hides some degree of flexibility and control from Kubernetes. You'd probably give higher resources to account for multiple workers. Then it may prevent Kubernetes from assigning the pod to existing nodes and may trigger the deployment of new nodes.

## Bonus: GZip Middleware for FastAPI
It seems that GZip middleware (that compresses request payload/body) is not enabled by default in FastAPI.
You need to explicitly add it to your application.

```Python
app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
```

([Source](https://github.com/kucukaslan/uvicorn-demo/blob/main/main.py#L43-L45))

It may reduce the response size significantly, obviously at the cost of some CPU time.
I've seen it reduce payload size from ~900 KB to ~175 KB. TBF, it was a relatively structured payload. It's on you to evaluate if it's worth it for your application.

JFYI, minimum_size argument is used to disable compression for smaller responses, compresslevel is the level of compression. 9 is the highest level.

## Bonus: JSON Serializer


## Demo Project

A complete working example implementing all the concepts discussed in this article is available in the [uvicorn-demo](https://github.com/kucukaslan/uvicorn-demo) repository. The project includes:

- Proper dependency configuration with `uvicorn[standard]` in [`pyproject.toml`](https://github.com/kucukaslan/uvicorn-demo/blob/main/pyproject.toml)
- Event loop verification in the [`lifespan` function](https://github.com/kucukaslan/uvicorn-demo/blob/main/main.py#L18-L43) to confirm uvloop and httptools usage
- Kubernetes-friendly [`Dockerfile`](https://github.com/kucukaslan/uvicorn-demo/blob/main/Dockerfile) with single-worker uvicorn setup
- GZip middleware configuration as shown above
- A `/large-response` endpoint for testing compression effectiveness with various payload sizes

## Last words
It's obviously on you to think about the graceful shutdown, observability integrations etc. 

I just wanted to comment on a few things that don't match with the natural assumptions.

Heads up: I also had some issues with using slim Docker images as they may not contain the necessary dependencies.
The demo project's Dockerfile installs the `build-essential` etc., but I couldn't reproduce the issue ( not downloading did not break).

I am not primarily a Python developer so I might be missing something. Moreover in my experience Python can be a magical language. 
So, there might be some magic under the hood that ensures the code/configuration you explicitly wrote is ignored in favor of some other preferred configuration. 