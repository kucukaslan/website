---
title: 'The Case Against ClusterIP: The Load Balancer That Never Was'
date: 2026-10-15T00:00:00+03:00
draft: false
tags: ['kubernetes', 'ingress', 'service-mesh', 'load-balancer']
language: en
content_type: technical
feature_image: img/case-against-clusterip-social.png
# series: ['series-name']
---

> TL;DR: ClusterIP distributes connections among server pods, while one would intuitively expect requests to be distributed among server pods. This difference leads to an imbalance in the number of requests handled by each pod. Hence, an uneven distribution of workload[^pedantic].

[^pedantic]: An imbalance in the number of requests handled does not necessarily mean an uneven distribution of workload, as the work done for each request may vary. But for God's sake, the correlation is almost 1!

It's, I guess, a K8s best practice to use ClusterIP for communication between internal services.
For most common HTTP services, especially those serving REST APIs, this best practice may inflict collateral damage on overall system health.

I'd like you to take a second[^not-literal] to think about how the connections and requests between the services are handled.  
How would you expect the distribution of the workload to be among server pods?  
What would be the distribution unit: connections or request, or something else?

## HTTP Requests and Connections

Let's take a step back and start with the simplest HTTP request lifecycle.
First, there should be a (TCP[^quic]) connection between the client and server.
So a connection must be opened first.
Then the client should send an HTTP request, and the server should respond.
Then, _optionally_, the connection is closed.
A crucial detail is that the client doesn't need to close the connection after receiving the response.
It can use the already established connection to send new requests.

So the most important *fact* I want to emphasize is this: *clients can issue multiple requests[^not-necessarily] over the same connection*.  
To reemphasize, one connection can be reused to send multiple requests.

The implications of this simple statement are why I call ClusterIP a load balancer that never was!

[^not-necessarily]: These requests are not necessarily concurrent or parallel.
[^quic]: HTTP/1 and HTTP/2 use TCP, while HTTP/3 uses QUIC (over UDP).

## ClusterIP and Connections

Let's consider client and server services in a K8s cluster. What happens when a client wants to issue a request?  
The client pod attempts to connect to `server.namespace.svc.cluster.local`. DNS resolves that name to the server service's virtual ClusterIP. When the client opens a TCP connection to that virtual IP, Kubernetes matches it with a specific pod.

Every request the client sends over that established connection reaches the same server pod.


{{< routing-visual kind="single-flow" >}}
The Service chooses a backend when the TCP flow is established. Reusing that flow also reuses the selected backend.
{{< /routing-visual >}}

A client can open multiple connections to the same service/server. In fact, most of the time, HTTP clients create a pool of connections to reuse. Each connection is associated with a single server pod. OK, would that solve the problem?

Let's say there are 10 server pods, and the client uses a connection pool of size five (i.e.&nbsp;five&nbsp;connections).  
Then, by the (dual) [pigeonhole principle](https://en.wikipedia.org/wiki/Pigeonhole_principle#Alternative_formulations:~:text=If%20n%20objects%20are%20distributed%20over%20m%20places%2C%20and%20if%20n%20%3C%20m%2C%20then%20some%20place%20receives%20no%20object.), there must be at least five server pods that receive no connections (i.e., no requests).

{{< routing-visual kind="five-of-ten" >}}
Even with no collisions between selections, five persistent connections can reach at most five of the ten pods.
{{< /routing-visual >}}

It's clear that when the number of connections is less than the number of server pods, some server pods won't receive any connections (i.e., no requests).
So those pods are unused, and their capacity is wasted.

What if the number of connections were to exceed the number of server pods?  
Would it suffice?  
***No!*** Let's assume there are 6 connections and 4 server pods. By the pigeonhole principle:

1. There exists at least one server that has at least two connections.
2. There exists at least one server that has at most one connection.  

∴ Hence, there exist two server pods, one with at least twice as many connections as the other (consequently receiving at least twice as many requests).

{{< routing-visual kind="six-over-four" >}}
This is the most even possible six-to-four assignment. Random server pod selection can make the difference larger, but not smaller.
{{< /routing-visual >}}

## How Does Ingress Fix the Problem?

<!--## How an HTTP-aware proxy relates to the problem-->
By accident?

We want the CPU/RAM usage of the server pods to be as close as possible.
If we know neither their current CPU/RAM usage nor how much an incoming request will affect it,
then the best heuristic (strongest correlation) we can use is the number of requests each server pod handles.
So we want to distribute the requests evenly among the pods.  
We discussed how ClusterIP does not reliably distribute requests equally, as it fixes the server pod when the connection is initialized.

So we need some way to distribute requests. A trivial solution is to disable connection reuse and force one connection per request. But this will add TCP connection overhead to every request, as well as require changes to the client code.

We need a layer between the client and the server that accepts and holds client connections but can distribute HTTP requests to the server pods, i.e., we need an HTTP-aware proxy[^L7-aware-proxy].

[^L7-aware-proxy]: It is also called something like *Layer 7 load balancing*. Saying *Layer 7* is way cooler, BTW.

Ingress comes to the rescue almost by accident.

Ingress is usually used to expose services to the outside world.
But it can also function as a load balancer that routes external traffic to internal services. And there is usually nothing stopping internal services from going through the Ingress.  
Unlike ClusterIP, Ingress can work at the HTTP level, i.e., it's HTTP-aware. Instead of distributing connections, it can distribute requests.  
Clients still establish reusable connections, but these connections are established between them and the Ingress (and not between them and the server pods).  
So clients won't need to make any changes to their code to use Ingress.  
They will still be able to use connection pooling and issue requests as they would with ClusterIP.
But the Ingress will distribute each request separately to the server pods regardless of the specific connection that request came from.


> The diagrams and comparison model persistent HTTP/1.1 with one in-flight request per connection, homogeneous pods, no retries or failures, and no session affinity.

{{< routing-visual kind="comparison" >}}
The comparison uses the same seeded workload on both sides. ClusterIP keeps five connections pinned to four pods; the illustrative HTTP proxy selects a backend per request using round robin.
{{< /routing-visual >}}

As you can see, the requests are distributed more evenly by the Ingress than by ClusterIP.

## Effects of Imbalance in Request Distribution

An obvious consequence is that some server pods will receive more requests than they can handle. Response times will increase (possibly causing timeouts). Depending on the K8s resource configuration, the corresponding server pod's CPU can get throttled, or the pod can even get killed due to OOM.

An indirect consequence is that even if the service gets a significant number of requests, the average resource (CPU/RAM) usage may remain relatively low. This may prevent scaling rules from being triggered to handle the increased load.  

I guess one may argue that the overloaded pods can have, for example, 200% CPU usage and still be able to trigger scaling rules based on CPU usage.  
This is fair, but it assumes that it is possible to hit 200% CPU usage. For this to happen:

1. The pod's CPU limits must be at least 2x its CPU requests (or shouldn't be set at all).
2. The node that _that pod_ is running on must have enough excess CPU capacity to allow that pod to use 2x its CPU requests.
3. Twice the requested CPU capacity must be practically usable. What I mean is that scripting languages used in backend services, like Python and Node.js, usually cannot utilize more than 1 CPU: Python due to its GIL, and Node.js due to its single-threaded event loop. So even if there is excess CPU capacity, the pod cannot utilize more than 1 CPU. So 1 CPU is a ceiling on how much CPU a pod can actually utilize with those languages.

...  
I admit that it is possible for this problem to be suppressed or insignificant under favorable conditions,
i.e., when constraints like those above don't apply.

## Reflections and Excuses

To be honest, this was one of the most convoluted problems I've dealt with.  
It took over three months from identifying the first significant symptoms to finding _the_ root cause and fixing it for good.  
I had my excuses:

- We didn't have historical metrics going back far enough to pinpoint the exact date the issues started (using a ClusterIP URL is the sane, default way).
- The average CPU/RAM usage and scaling seemed fine. I ascribed the MAX CPU usage to excessive CPU usage during initialization: with 100+ concurrent pods scaling up and down throughout the day, that seemed reasonable.
- The request traces weren't useful [e.g., by default, they cannot properly attribute "short"[^short] (<50/100 ms) or discontinuous Python event loop waits].
- We immediately applied a few workarounds that mitigated/suppressed the issue sufficiently to make time for higher-priority tasks at hand.
- Neither the use of ClusterIP (internal service URLs) nor connection pooling was an explicit decision. They were both *obvious* defaults.

And the strongest excuse is that, as it turned out, the root cause was not directly related to the affected application itself.
There were many real hot paths we were continuously improving, so it was more plausible that one of those hot paths was causing such trouble.
Moreover, there was (practically) no one who decided to use connection pools and/or ClusterIPs; they're (practically) the default options
for HTTP clients and Kubernetes. Since no one made a decision about them, no one thought about them and their risks either—until they bit us in the behind.

## Last Words

> No **service** is an Iland, intire of itselfe; every **service**  
is a peece of the **system**, a part of the maine;

It's an admirable, albeit vain, endeavour to separate services (parts) from the system (whole).
Services function as part of the whole system, affecting and being affected by how each part interacts with the others in the system.


Technically speaking, there were no problems with:
- The applications themselves[^beside]: they responsibly reused the established TCP connections for multiple requests.
- Kubernetes' ClusterIP: it gave pod IPs evenly across connections.

Similarly, no team made any mistakes: both application and infrastructure developers used the sane defaults.

Then what failed? It was the _way_ the parts interacted with and impacted each other.
Each part performed as expected, but the whole system did not.

Since ownership was tied to the individual parts,
ownership of and responsibility for the relations between the parts were unclaimed, uncontested, and unquestioned.
It was both everyone's and no one's responsibility to understand how connection pooling works with Kubernetes ClusterIPs.

We can draw boundaries, beautiful and elegant boundaries, around parts and their ownership as much as we want.  
However, the system won't care about our boundaries; it will work as a whole, with both its parts and their relations.

For better or worse.

[^beside]: Aside from being written in Python, running the risk of doing significant CPU work (>1 ms, depending on the request) in the main event loop, and having dozens of other problems.
<!--
We cannot fully delegate understanding of how our services interact with other services in the system.
We still need to study and understand the system that our application is part of[^grammar-nazi].
[^grammar-nazi]: yes, I ended the sentence with a preposition, deal with it.-->



[^short]: Not that I think 50 ms is short in any sense.
[^not-literal]: You can take more time if you want; I don't think a second would be enough.
