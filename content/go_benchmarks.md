---
title: "A Commentary on Go Webserver Benchmarks"
date: 2024-09-08T00:00:01+03:00
tags: ['go', 'english', 'benchmarks', 'technical']
draft: true
---

> TLDR is TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that faster for you.

> TLDR: [Fiber](https://github.com/gofiber/fiber) is not going to be that faster in your case unless 
you can explain what particular feature of fiber will be advantageous
for your specific use case.

Let's start with the famous graph from  its [homepage](https://gofiber.io/assets/images/benchmark-pipeline.png):
![Benchmark Graph with HTTP Pipelining where fiber is by far superior to the most of the alternatives even with 500ms jobs](/img/benchmark-pipeline.png)

This graph obviously[^ack] proves that fiber can serve 10 times of the requests 
that net/http ("default"), chi, gin etc. can, and this is not affected by
how much "business logic" takes (i.e. time spend for each request).

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

Then what is the problem?







This article is dedicated to relentless proponents of [Fiber](https://github.com/gofiber/fiber),
and [Cunningham's Law](https://letmegooglethat.com/?q=Cunningham%27s+Law).


