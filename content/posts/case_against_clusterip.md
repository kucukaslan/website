---
title: 'Case Against ClusterIP: Load Balancer That Never Was'
date: 2026-08-31T00:00:00+03:00
draft: false
tags: ['kubernetes', 'ingress', 'service-mesh', 'load-balancer']
language: en
content_type: technical
feature_image: img/case-against-clusterip-social.png
# series: ['series-name']
---
> This is a draft of an upcoming post. Feel free to mail me muhammed@kucukaslan.com.tr or schedule a meeting via [meet](./about)

> TL;DR: ClusterIP distributes connections among server pods, while one would intuitively expect requests to be distributed among server pods. This difference leads to imbalance in the number of requests handled by each pod. Hence, uneven distribution of workload[^pedantic].

[^pedantic]: imbalance of the number of requests handled does not necessarily mean uneven distribution of workload as the work done for each request may vary. But for God's sake, the correlation is almost 1!

It's, I guess, a K8s best practice to use ClusterIP for communications between the internal services.
For most common HTTP services, esp. those serving RESTs, this best practice may inflict collateral damage to overall system health.

I'd like you to take a second[^not-literal] to think about how the connections and requests between the services are handled.  
How would you expect the distribution of the workload to be among server pods?  
What would be the distribution unit: connections or request, or something else?

## HTTP Requests and Connections
Let's take a step back and start with simplest HTTP request lifecycle.
First, there should be a (TCP[^quic]) connection between the client and server.
So a connection must be opened, first.
Then the client should send an HTTP request and the server should respond.
Then, _optionally_, the connection is closed.
Crucial detail is that, client doesn't need to close the connection after the receiving the response.
It can use, already established, connection to send new requests.

So most important *fact* I want to acknowledge is that: *clients can issue multiple requests[^not-necessarily] over the same connection*.  
Reemphasizing, one connection can be reused to send multiple requests.

Implications of this simple statement is why I call ClusterIP a load balancer that never was!

[^not-necessarily]: that are not necessarily conccurent or parallel
[^quic]: HTTP/1 and HTTP/2 use TCP, while HTTP/3 uses QUIC (over UDP).
## ClusterIP and Connections
Let's consider client and server services in a K8s cluster. What happens when a client wants to issue a request?
The client pod attempts to connect to `server.namespace.svc.cluster.local`. For a normal (non-headless) Service, DNS resolves that name to the Service's virtual ClusterIP—not to one of the pod IPs. When the client opens a TCP connection to that virtual IP, the Kubernetes Service data path selects an endpoint and redirects the flow to it.[^virtual-ip]

Every request the client sends over that established connection reaches the same server pod.

[^virtual-ip]: The exact data path depends on the cluster's networking implementation. The common `kube-proxy` modes implement the same basic virtual-IP behavior: traffic to a Service's ClusterIP and port is redirected to an endpoint. See [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/).

{{< routing-visual kind="single-flow" >}}
The Service chooses a backend when the TCP flow is established. Reusing that flow also reuses the selected backend.
{{< /routing-visual >}}

A client can open multiple connections to the same service/server. In fact most of the time http clients creates a pool of connections to reuse. Each connection is associated with a single server pod. Ok, would that solve the problem?

Let's say there are 10 server pods and client uses a connection pool of size 5 (i.e. 5 connections).  
Then, by the (dual) [pigeon hole principle](https://en.wikipedia.org/wiki/Pigeonhole_principle#Alternative_formulations:~:text=If%20n%20objects%20are%20distributed%20over%20m%20places%2C%20and%20if%20n%20%3C%20m%2C%20then%20some%20place%20receives%20no%20object.), there must be at least five server pods that receive no connection (i.e. no request).

{{< routing-visual kind="five-of-ten" >}}
Even with no collisions between selections, five persistent connections can reach at most five of the ten pods.
{{< /routing-visual >}}

It's clear that when the number of connections is less than the number of server pods, some server pods won't receive any connections (i.e. no request).
So those pods are not utilized/wasted.

What if the number of connections were to exceed the number of server pods?  
Would it suffice?  
No! Let's assume there are 6 connections and 4 server pods. By the pigeon hole principle: 
1. There exists at least one server that has at least two connections.
2. There exists at least one server that has at most one connection.
Hence, there exists two server pods, one with at least double the connections of the other (consequently receiving at least double the requests).

{{< routing-visual kind="six-over-four" >}}
This is the most even possible six-to-four assignment. Random endpoint selection can make the difference larger, but not smaller.
{{< /routing-visual >}}

## How an HTTP-aware proxy relates to the problem
We want the number of requests each server pods to be equal.
We discussed that ClusterIP does not reliably distribute the requests equally.

So we need some way to distribute requests. A trivial solution is to disable connection reuse and force 1 connection 1 request. But this will add TCP connection overhead on top of every request as well as requiring changes to the client code.

We need a layer between the client and the server that accepts and holds client connections but can distribute HTTP requests to the server pods. An HTTP-aware proxy—such as the data plane run by an Ingress controller—can fill this role.

The Ingress resource itself is configuration; the controller or proxy is what handles the traffic. Ingress controllers are usually deployed to expose services outside the cluster, but an internal client can also be routed through an appropriately configured proxy.

The client can still establish reusable connections, except those connections terminate at the proxy rather than at the server pods. Because the proxy understands HTTP, it can select an upstream for each request, regardless of which client connection carried that request. The exact algorithm and connection-reuse behavior depend on the proxy and its configuration.

> The diagrams and comparison model persistent HTTP/1.1 with one in-flight request per connection, homogeneous pods, no retries or failures, and no session affinity.

{{< routing-visual kind="comparison" >}}
The comparison uses the same seeded workload on both sides. ClusterIP keeps five connections pinned to four pods; the illustrative HTTP proxy selects a backend per request using round robin.
{{< /routing-visual >}}

As you can see, the requests are distributed more evenly by the Ingress than by ClusterIP.

## Effects of Imbalance in Request Distribution
An obvious consequence is that some server pods will receive more requests than they can handle. Response times will increase (possibly causing timeouts), depending on the K8s resource configuration the corresponding server pod CPU can get throttled or the pod even get killed due to OOM.

An indirect consequence is that even if the service gets a significant amount of requests, the average resource (CPU/RAM) usage may remain relatively low. This may avoid scaling rules that would be triggered to handle the increased load.  
I guess, one may argue that the overloaded pods can have for example 200% CPU usage and still be able to trigger scaling rules based on CPU usage.  
This is fair, but it assumes that it is possible to hit 200% CPU usage. For this to happen:
1. The pod CPU limits must be at least 2x the pod CPU requests (or shouldn't be set at all)
2. The Node that that pod is running on must have enough excess CPU capacity to allow that pod to exceed its CPU requests by 2x
3. 2x of the requested CPU capacity must be practically usable. What I mean is that: scripting languages, that happens to be used in backend serveices, like Python and Node.js usually cannot utilize more than 1 CPU. Python due to its GIL, and Node.js due to its is single-threaded event loop.

So what happens usually is that there is both low average CPU usage across pods, while a significant number of requests are either timed-out or has high latency.


[^not-literal]: you can take more time if you want, I don't think a second would be enough
