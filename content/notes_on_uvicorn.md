---
title: "Notes on Uvicorn on Production"
date: 2025-10-29T00:00:00+03:00
tags: ['en', 'python', 'uvicorn', 'fastapi', 'production']
draft: false
---

The uvicorn + fastapi is a common default stack for Python web applications.
However, it is easy to use it incorrectly on the production environment.
A naive person could would install the fastapi and uvicorn using the `pip install fastapi uvicorn` (or `uv add fastapi uvicorn`) command.
This is not incorrect and it will work, but it leaves low hanging fruits untouched.

## uvloop and httptools
However, when uvicorn is installed this way, it uses the `asyncio`'s default event loop for corresponding platform, which is usually a pure python implementation.

Remember the rule of thumb for Python is **avoid pure python implementation of anything**,
not even the freaking `for` loops are exception (use numpy, pandas, etc. where possible).

So, we can't, in our right mind, use the that pure python event loop.
Luckily, there is a common suggested non-python event loop implementation: `uvloop`.
It is included in the uvicorn's standard dependencies, so we can just install it using the `uv add 'uvloop[standard]'` command.

Similarly, by default uvicorn uses some pure python http parser. Again, there is a non-python http parser implementation: `httptools` which is also included in the uvicorn[standard] dependencies.

## Don't Use Gunicorn on Kubernetes, Don't Multiple Workers
The natural next step following the protypeing the python server is to Dockerize it to be deployed in the production environment possibly on a Kubernetes cluster.

Now, that you've seen the naive mistake in installing uvicorn, you might want to be smart before you prepare production configuration and made some research.

You possibly asked some famous LLMs or even found [uvicorn.dev/deployment](https://uvicorn.dev/deployment/) and actually read the documentation by yourself like the old people.

Right there, in the official documentation, you see the following advice:
> Run `gunicorn -k uvicorn.workers.UvicornWorker` for production.

or see
> gunicorn -w 4 -k uvicorn.workers.UvicornWorker


below. Don't do it.
Not because it's wrong.
In fact this suggestion is great -but for the old-school reliable deployments to dedicated servers.

Gunicorn is yet another layer on top of the server.
It's used to manage multiple copies of the server in the same machine: distribute the load among them, restart them if they crash, etc.

When you deploy your application to a Kubernetes cluster, you already have a layer of load balancing and scaling. If you need multiple copies of the server, you should use multiple Kubernetes Pods. Kubernetes can manage it as well as Gunicorn can. Also, with kubernetes you get to deploy them on different nodes, and deploy other services on the same nodes.

If Gunicorn is used with kubernetes, then it hides some degree of flexibility and control from kubernetes. You'd probably give higher resources to account for multiple workers. Then it may prevent kubernetes from assigning the pod to existing nodes and trigger the deployment of new nodes.

## Bonus: GZip Middleware
It seems that GZip middleware (that compressses request payload/body) is not enabled by default in the uvicorn.
You need to add it manually to your application.
```python
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
```

It may reduce the response size significantly, obviously at the cost of some CPU time.
I've seen it to reduce payload size from ~900 KB to ~175 KB. TBF, it was relatively structered payload. It's on you to evaluate if it's worth it for your application.

JFYI, minimum_size argument is used to disable compression for smaller responses, compresslevel is the level of compression. 9 is the highest level.

## Last words
It's obviously on you to think about the graceful shutdown, observability integrations etc. 

I just wanted to comment on a few things that doesn't match with the natural assumptions.