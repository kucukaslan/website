---
title: "A Rant on Go Fiber's Infamous Chart: Benchmarking Web Frameworks"
date: 2026-08-23T00:00:00+03:00
tags: ['go', 'benchmarks']
draft: false
# url: /go_benchmarks/
language: en
content_type: technical
---

> TLDR is TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that much faster for you.

> TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that much faster in your case unless 
you can explain what particular feature of Fiber will be advantageous
for your specific use case.

Let's start with the infamous chart from their [homepage](https://gofiber.io/img/benchmark-pipeline.png):
![Benchmark chart with HTTP pipelining where Fiber is far superior to most alternatives, even with 500 ms jobs](/img/benchmark-pipeline.png)

This chart obviously[^ack] proves that Fiber can serve 10 times as many requests 
as net/http ("default"), chi, gin, etc. can, and this is not affected by
how long the "business logic" takes [i.e. the response time (?) of each request].

Well, actually no!
[^ack]: I reserve the right to retract the acknowledgements above, since they simulated 
 time spent on the business logic with [time.Sleep](https://github.com/smallnest/go-web-framework-benchmark/blob/b07cebd150aa2458ba2df1726a284ea4fd36fad4/server.go#L407).
 The `time.Sleep` does not block the CPU AFAIK.
 So sleeping 500 ms and using CPU for 500 ms are different things [^sleep].

[^sleep]: I benchmarked it, and it takes "3194 ns/op" per 500 ms sleep.
    ```go
    func BenchmarkSleep(b *testing.B) {
        wg := sync.WaitGroup{}
        for i := 0; i < b.N; i++ {
            wg.Add(1)
            go func() {
                defer wg.Done()
                time.Sleep(500 * time.Millisecond)
            }()
        }
        wg.Wait()
    }
    ```

## Then What Is the Problem?
It is about what is being measured.

### time.Sleep
First of all, it's simulating the business logic with [time.Sleep](https://pkg.go.dev/time#Sleep),
so if your business logic does anything beyond sleeping 
between accepting a request and responding, this chart will be _misleading_.

### HTTP Pipelining
Second, this specific benchmark uses HTTP pipelining!

Have you ever heard of it?
Is this the first time you've heard of it?
Did you learn about it in a networking course at university and then totally forget about it?

If, at the very least, you don't remember the word `pipeline` from 
the HTTP client config you prepared[^have_ai_prepared], probably you are not using it at all.
[^have_ai_prepared]: configs you had AI/LLMs prepare

Whether you realize it or not, you are probably not using Fiber with HTTP pipelining. 
In fact, many common HTTP client libraries intentionally do not support HTTP pipelining, including:
- Python: 
  - [aiohttp](https://docs.aiohttp.org/en/latest/client_advanced.html?#http-pipelining)
  - [HTTPX / httpcore](https://github.com/encode/httpcore/discussions/505?#:~:text=Active%20connections%20will%20only%20ever%20have%20one%20request%20for%20HTTP/1.1)
- Java:
  - [OKHTTP](https://github.com/lysine-dev/okhttp/issues/4066#:~:text=Pipelining%20is%20a%20great%20idea%20but%20not%20reliable%20in%20practice.%20You%20should%20probably%20just%20make%20your%20calls%20in%20serial%20and%20ask%20your%20server%20team%20to%20fix%20their%20stuff.) "Pipelining is a great idea but not reliable in practice. You should probably just make your calls in serial and ask your server team to fix their stuff."
- Node.js:
  - [undici](https://github.com/nodejs/undici/blob/main/docs/docs/api/Client.md?utm_source=chatgpt.com#:~:text=Pipelining%20is%20disabled%20by%20default.) (the [fetch()](https://undici.nodejs.org/#:~:text=Node.js%20includes%20a%20built%2Din%20fetch()%20implementation%20powered%20by%20undici%20starting%20from%20Node.js%20v18.)): Pipelining is disabled by default.
- Go: 
  - [net/http](https://github.com/golang/go/discussions/60746#:~:text=There%20is%20no%20equivalent%20to%20this%20setting%20for%20HTTP/1%20connections%2C%20which%20only%20support%20a%20single%20concurrent%20request%20per%20connection.)
  - fasthttp supports via [PipelineClient](https://pkg.go.dev/github.com/valyala/fasthttp?utm_source=chatgpt.com#PipelineClient) but warns "[fasthttp might not be for you!](https://github.com/valyala/fasthttp#fasthttp-might-not-be-for-you)"

Moreover, Go’s standard library server accepts pipelined requests but processes them [serially](https://github.com/golang/go/blob/go1.27.0/src/net/http/server.go#L2129-L2135). lol, lmao even.
> HTTP cannot have multiple simultaneous active requests. \
Until the server replies to this request, it can't read another, ... \
we're not going to implement HTTP pipelining because it
was never deployed in the wild and the answer is HTTP/2.

So, pipelining is largely abandoned —[^emdash]for good reasons!

[^emdash]: this emdash is technically AI generated,
I wasn't aware at the time that Option+Shift+Hyphen is the emdash shortcut in MacOS,
so I just googled `emdash` and copied it from an AI overview.

The number-one reason is head-of-line blocking (for responses)!
A slow or blocked request at the head of the (pipe)line can block all the requests coming after it.  
So, pipelining, practically, at best, somewhat improves the performance
but when it goes wrong it makes things much worse.  
For reasons like this, it never became popular and was superseded by multiplexing in HTTP/2.

Since, practically speaking, pipelining is not used anywhere, it is a bad metric to bench against.

More on the HTTP Pipelining and Benchmarks:
> HTTP Pipelining is useless and please **stop publishing benchmarks with Pipelining enabled. It’s just lying about real-world performance**...  
Pipelining will not help serve more requests
https://deavid.wordpress.com/2019/10/06/http-pipelining-is-useless/

More on head-of-line blocking and, in particular, how HTTP/1.1 pipelining is affected by it: 
> pipelining solves HOL blocking for requests, but not for responses  
... [t]o make matters worse, most browsers actually do not use HTTP/1.1 pipelining in practice
https://calendar.perfplanet.com/2020/head-of-line-blocking-in-quic-and-http-3-the-details/#sec_pipelining

## Simulating the Work with time.Sleep
Now, we can return to the [sleep](https://pkg.go.dev/time#Sleep)ing issue.
Think about what your services do to process a request in a real production environment.
I'd assume it doesn't merely sleep unless you are using
all-in-all microservice architecture 
and split all the `time.Sleep`s into a dedicated microservice
of its own along with its own database clusters, its own ValKey etc. full setup…

Fine, fine, you didn't come to read my sarcasm...

### Request's Workload
An ordinary backend service usually does some mixture of:
* Sleep (lol): Yes, nobody is stopping you from writing a sleeping service.
* I/O operations:
  * Network I/O: 
    * Call other services (HTTP, gRPC etc.)
    * Querying database: SQL, NoSQL, Redis etc.
  * Filesystem I/O    
    * reading files
    * writing files
    * writing logs synchronously (if it were async, you wouldn't wait for it)
    * SQLite (You thought it was included in "_Querying database_", didn't you?)
* CPU-bound operations:
  * Floating-Point Operations as in FLOPS (I mentioned it because it sounds cooler than general computations)
  * JSON/protobuf parsing and serialization
  * usual business code: conditionals, mappings, filters, sorting, mandatory [isRecord](https://x.com/tldraw/article/2075329561642840339) check
  * ML inference (AI)
* Waiting for Resources and System Overheads:
  * the event loop (especially for Python and Node.js services)
  * server's concurrency limits, e.g. https://uvicorn.dev/server-behavior/#resource-limits 
  * connection pools: aiohttp, DB connection pools etc.
  * open file limits
  * memory allocations
  * garbage collections
  * logging/telemetry instrumentation
  * language/framework overheads

How does each one of them affect the number of requests your service can serve per second (or per minute, i.e. its throughput)?

### CPU
The first physical/hard limitation is the CPU.
You can use a CPU at most one second per second, duh.

Let's define the amount of work a specific CPU can do in a second as 1 CPU*second
(less informally we could use # of CPU cycles).

That means if a request does 1 milli CPU*second of CPU work
(i.e. actively uses/occupies the CPU for exactly one millisecond), 
then you can, at best, serve at most 1,000 requests per second (RPS).
You can't defeat classical physics —[^emdash-handwritten]not sure about the quantum or the meta.
[^emdash-handwritten]: this emdash was handwritten.

### Resource Limits
This is the second one.

Do you have any pools for database or HTTP connections?  
Do you open files?
In many Linux distributions, there is a 1,024-open-file limit per process. 
That is, your app can open at most 1,024 files simultaneously[^per-process] 
[^per-process]: per process. A backend service might have multiple processes I guess. 

So, if every request opens a file, spends one millisecond, and closes it,
then this can be repeated at most a thousand times in a second.  
Assuming you can do this for 1024 files simultaneously,
you then have a theoretical limit of at most 1,024,000 RPS.

Obviously, if you open a file you will use it so this theoretical limit is out of reach.
But this usage will make CPU operations the bottleneck, and we already discussed that.

The same goes for all kinds of connection pooling, concurrency limits, semaphores, etc.

### I/O Operations
Now, let's examine I/O operations:  
As far as I'm concerned, we can group I/O operations into two groups: those using the same CPU (and resources) as the service and others (external I/O).[^pedantic-cpu]
[^pedantic-cpu]: if you want to be [pedantic](https://i.redd.it/a6ut63j7gaq41.png), all of them use the CPU for some amount of time, but I felt it was worth distinguishing them, as the amount of direct CPU work required differs significantly among these categories. Please don't come and tell me that downloading hundreds of petabytes of data over the network uses more CPU*time than computing the determinant of a 2x2 matrix in a dedicated process pool.

In languages like Python and Node.js 
it is customary to have a dedicated process/worker pool 
to offload CPU operations
to avoid blocking the CPU in the main event loop.
Although they do not block the main event loop,
they still compete with it for the CPU time (and the GIL for python).  
These kinds of I/O operations are more closely related
to the CPU limitations (and the resource limitations) discussed earlier.

On the other hand, external I/O operations are bounded 
by the limitations of the external services, DBs etc.  
The amount of CPU work is usually negligible,
so we generally assume that external parties 
are not the bottleneck.
We assume they have unlimited resources 
and can handle whatever the load amounts to. 
Probably because it's hard to estimate their capabilities
and they are hardly ever the bottleneck.
However, when they are the bottleneck, your clients/customers will notice before you do :lol:

### System Overheads
And finally the system overheads:
There are 
- OS-level overheads, 
- process/thread scheduling, 
- memory allocations, 
- syscalls,
- telemetry/observability instrumentation,
- garbage collection
and yours truly:
- web server framework overheads.

Finally, this is where all these shiny web frameworks
will or would differ if they do differ and if the differences matter.
The framework determines how requests are routed, how middleware is organized, and which HTTP/gRPC protocols are used or implemented, etc.  
Hence, framework performance will matter only as much as these functions matter to your service's performance.

## Evaluating Framework Performance for Your Needs 
In order to evaluate how much framework selection will affect your service's performance, 
first you should find what your bottleneck is.  
After all, the service will be only as fast as its slowest part.  
You might not be able to answer this definitively in advance, 
so you need to take advantage of your past experience
that trained your instincts and formed your taste.  
If you haven't acquired them yet, you are lucky to learn them along the way;
still, you can consult your colleagues, seniors and of course our AI overlords!

Anyway, once you have some idea about your probable bottlenecks,
you can examine all the benchmark variations by [smallnest](https://github.com/smallnest/go-web-framework-benchmark/tree/master#basic-test), from which the infamous chart was taken (?).[^source]
[^source]: trust me bro.  
I decided to write a post about this around September 2024 and noted this repo as the source for the benchmark.
But I'm not sure whether it was really taken from there.


Nowadays, most of my work is on services that process CPU-heavy requests,
so I want to include the benchmark for CPU-bound operations.
![CPU Bound Benchmark](https://github.com/smallnest/go-web-framework-benchmark/blob/master/cpubound_benchmark.png?raw=true)
As you can easily see, adjusting for the y-axis crime,
there isn't much difference among the listed web frameworks.
Upper bound is 1360, lower bound is 1160.
So the throughput is at most 17% higher.
Remembering from the earlier discussion on CPU bound operations,
we can guess that it assumes a CPU job that takes 1 ms worth of all available compute.
When operating on large matrices, as one would need in duration/distance matrices, mathematical solvers, or ML model inference,
one usually needs more than 1ms worth of compute (unless the operation is not offloaded to the GPUs).
So these numbers get smaller, and the gap between the frameworks gets narrower (both in absolute and relative terms).

## Conclusion and the Return of the Prodigal Developer
I'm not writing a new microservice every other day,
but I must admit that I've chosen Fiber multiple times.  
If someone were to ask me which web framework to use,
I would say use the standard library, Fiber, chi, gin, or whatever looks more usable/familiar to you.  
I believe that when our service's workload and bottlenecks are not clear to us,
or when we don't have sufficient knowledge
about how these frameworks differ
and what the major shortcomings of each are,
it is wiser to choose one of the most popular frameworks.  
At that point, we don't have enough information to make the ideal/correct choice,
so our choice is likely to be suboptimal.
Choosing a framework that is bad for our use case is much worse than choosing a popular framework that is not the best but is sufficiently good.[^local-maxima]
[^local-maxima]: OTOH, if we make a sufficiently good decision we get stuck in the local maxima,
but if we make a bad decision we may get to make a rewrite to strengthen our performance review case and our CV.
As you see, there are many trade-offs to make...

Finally, I want to dedicate this post to relentless proponents of [Fiber](https://github.com/gofiber/fiber),
and [Cunningham's Law](https://letmegooglethat.com/?q=Cunningham%27s+Law).
