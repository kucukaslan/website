---
title: "A Rant on Go Fiber's Infamous Chart: Benchmarking Web Frameworks"
date: 2026-08-23T00:00:00+03:00
tags: ['go', 'benchmarks']
draft: true
# url: /go_benchmarks/
language: en
content_type: technical
---

> TLDR is TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that faster for you.

> TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that faster in your case unless 
you can explain what particular feature of Fiber will be advantageous
for your specific use case.

Let's start with the famous graph from their [homepage](https://gofiber.io/img/benchmark-pipeline.png):
![Benchmark Graph with HTTP Pipelining where fiber is by far superior to the most of the alternatives even with 500ms jobs](/img/benchmark-pipeline.png)

This graph obviously[^ack] proves that Fiber can serve 10 times the requests 
that net/http ("default"), chi, gin etc. can, and this is not affected by
how much "business logic" takes [i.e. response time (?) of each request].

Well, actually no!
[^ack]: I reserve my right to retract the acknowledgements above, since they simulated 
 time spent on the business logic with [time.Sleep](https://github.com/smallnest/go-web-framework-benchmark/blob/b07cebd150aa2458ba2df1726a284ea4fd36fad4/server.go#L407).
 The `time.Sleep` does not block CPU AFAIK.
 So sleeping 500 ms and using CPU for 500 ms are different things [^sleep].

[^sleep]: I benchmarked and it takes "3194 ns/op" per 500 ms sleep.
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
First of all, it's simulating the business logic with [time.Sleep](https://pkg.go.dev/time#Sleep)
so if your business logic does anything beyond sleeping 
between accepting the request until responding, this chart will be _misleading_.

### HTTP Pipelining
Second, this specific benchmark uses HTTP pipelining!

Have you ever heard about it?
Is it the first time hearing about it?
Did you learn it in the network course in university then totally forget about it?

If, at the very least, you don't remember the word `pipeline` from 
the HTTP client config you prepared[^have_ai_prepared], probably you are not using it at all.
[^have_ai_prepared]: configs you had AI/LLMs prepare

Whether you were aware or not you are not using the fiber with pipelines. 
In fact many common HTTP client libraries intentionally does not support HTTP pipelining including but not limited to
- Python: 
  - [aiothttp](https://docs.aiohttp.org/en/latest/client_advanced.html?#http-pipelining)
  - [HTTPX / httpcore](https://github.com/encode/httpcore/discussions/505?#:~:text=Active%20connections%20will%20only%20ever%20have%20one%20request%20for%20HTTP/1.1)
- Java:
  - [OKHTTP](https://github.com/lysine-dev/okhttp/issues/4066#:~:text=Pipelining%20is%20a%20great%20idea%20but%20not%20reliable%20in%20practice.%20You%20should%20probably%20just%20make%20your%20calls%20in%20serial%20and%20ask%20your%20server%20team%20to%20fix%20their%20stuff.) "Pipelining is a great idea but not reliable in practice. You should probably just make your calls in serial and ask your server team to fix their stuff."
- Node.js:
  - [undici](https://github.com/nodejs/undici/blob/main/docs/docs/api/Client.md?utm_source=chatgpt.com#:~:text=Pipelining%20is%20disabled%20by%20default.) (the [fetch()](https://undici.nodejs.org/#:~:text=Node.js%20includes%20a%20built%2Din%20fetch()%20implementation%20powered%20by%20undici%20starting%20from%20Node.js%20v18.)): Pipelining is disabled by default.
- Go: 
  - [net/http](https://github.com/golang/go/discussions/60746#:~:text=There%20is%20no%20equivalent%20to%20this%20setting%20for%20HTTP/1%20connections%2C%20which%20only%20support%20a%20single%20concurrent%20request%20per%20connection.)
  - fasthttp supports via [PipelineClient](https://pkg.go.dev/github.com/valyala/fasthttp?utm_source=chatgpt.com#PipelineClient) but warns "[fasthttp might not be for you!](https://github.com/valyala/fasthttp#fasthttp-might-not-be-for-you)"

Moreover Go’s standard library server accepts pipelined requests but process them [serially](https://github.com/golang/go/blob/go1.27.0/src/net/http/server.go#L2129-L2135). lol, lmao even.
> HTTP cannot have multiple simultaneous active requests. \
Until the server replies to this request, it can't read another, ... \
we're not going to implement HTTP pipelining because it
was never deployed in the wild and the answer is HTTP/2.


Pipelining is largely abandoned, for good reasons!

#1 reason being the head of line blocking (per responses)!
A slow or blocked request at the head of the (pipe)line can block all the requests coming after it.  
So, pipelining, practically, at best, somewhat improves the performance but when it goes wrong it makes things terribly worse.
Since it is not practically used, it is a bad metric to bench for.

More on the HTTP Pipelining and Benchmarks:
> HTTP Pipelining is useless and please **stop publishing benchmarks with Pipelining enabled. It’s just lying about real-world performance**...  
Pipelining will not help serve more requests
https://deavid.wordpress.com/2019/10/06/http-pipelining-is-useless/

More on Head of line blocking and in particular how HTTP/1.1. Pipelining is affected by it: 
> pipelining solves HOL blocking for requests, but not for responses  
... [t]o make matters worse, most browsers actually do not use HTTP/1.1 pipelining in practice
https://calendar.perfplanet.com/2020/head-of-line-blocking-in-quic-and-http-3-the-details/#sec_pipelining

## Simulating the Work By time.Sleep
Now we can return to the sleeping issue think about what your services do to process a request in reality I assume it doesn't merely sleep unless you are using all in all microservice architecture and Split all the time slip in locations into a dedicated microservices of its own along with it's all on database clusters credits Etc full setup…
Heart, fine you didn't came to read my sarcasm
An ordinary service usually do some of 
Sleep
I/O operations
CPU Bond operations

fill from the notes

How do this affect how many requests in your service can serve in a time interval in a second
First physical limitation is the CPU. you can only make one CPU second amount of work in a second. that is if your request actively uses/occupies  the CPU For exactly one milliseconds you can at Birth so at most 1,000 requests. you can't defeat the classical physics, not sure about the quantum one or the meta one.
 second one is the resource limit. do you have any pools for database or HTTP connections?
Do you open files? in many Linux distributions there is a thousand and 24 open file limit. that is you can open at most 1024 files simultaneously 
So If you open a file, spend one millisecond, and close it then you can repeat this a thousand times a second. assuming you can do this for 1024 files simultaneously done you have at Max want me on request per second theoretical limit. 
 obviously if you open a file you will use it so this certificate limit is Out Of Reach but this related to CPU operations you would need and we already discussed it
Same goes for all kind of connection pullings concurrency limits semaphors Etc.
 now last examine IO operations we can rock the group I operations into doors use the same CPU with the service and others. if you want to be pedantic all of them use same CPU for some amount of time but the distinction the distinction is based on the significance based on the amount of CPU work required to achieve this task period new line in languages like Python and Node.js  it is customary to have a dedicated process / workers pool to offload CPU operations to avoid blocking the CPU in the Main Event loop.
 this kind of I operations obviously brings back the CPU limitations and discussed earlier.
 for external IO operations we are bounded by the Limited limitations of the external service it may be a TV Etc.
It goes without saying that there is some amount of work at least sending writing a request and receiving reading response but it's negligible we usually assume that external parties are not the bottleneck they have unlimited resources and they can handle the lot whatever it amouns to,  since it's hard to estimate their capabilities and they are hardly ever the bottleneck, but when they are the bottleneck; your clients / customers will notice before you do call an ambulance
And the overheads:
 always level overheads, process / threat scheduling, no matter allocations, cisco's, any Telemetry / observability instrumentations, garbage collection, and yours truly:
Web server framework overheads.
 So finally this is where all these shiny web Frameworks will differ if they do differ and if the differences matter.
First thing you should find is what your bottleneck is. after all the service will be as fast as its slowest part.
 you might not be able to definitely answer this in advance; so you need to take advantage of your past experience that trained your instincts and formed your taste. if you don't have it yet you are lucky to learn it along the way; all consult your colleagues, seniors and of course our AI overlords!
Anyway once you have some idea about your probable bottlenecks you can examine the full Benchmark that the infamous chart was taken.
 most of my work is processing CPU heavy request so I want to include the Benchmark for CPU band operations as you can easily see any once you realize that why axis starts there isn't much a difference among the listed web Frameworks.



This article is dedicated to relentless proponents of [Fiber](https://github.com/gofiber/fiber),
and [Cunningham's Law](https://letmegooglethat.com/?q=Cunningham%27s+Law).

https://chatgpt.com/s/t_6a88c9a185d88191a7519aa309064e57
https://go.dev/src/net/http/server.go?s=70171%3A70186&utm_source=chatgpt.com#:~:text=//%20But%20we%27re%20not,is%20HTTP/2.



https://github.com/smallnest/go-web-framework-benchmark/tree/b07cebd150aa2458ba2df1726a284ea4fd36fad4
