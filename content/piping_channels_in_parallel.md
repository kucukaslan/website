---
title: "A story of race conditions when piping channels in parallel"
date: 2025-05-28T23:22:02+03:00
tags: ['professional', 'english']
draft: true
---

I had to write a batch processing job that downloads multiple files,
processes them separately using external services, 
and produces separate outputs for each file.

Ah the classical SIMD problem, I thought. \
We[^royal] are gonna have fun with all that *channel*s, *sync*s, *once.Do*s and *goroutine*s; I thought. \
But man[^person], was I wrong.

[^royal]: pluralis majestatis
[^person]: as in the [God gesceop ða æt fruman twegen _**men**_, wer and wif](https://en.wikipedia.org/wiki/Man_(word)) 


```mermaid
flowchart TD
    A[Start] --> B{Is the channel open?}
    B -- Yes --> C[Read from channel]
    C --> D{Is the data valid?}
    D -- Yes --> E[Process data]
    E --> F[Write to output]
    F --> G[Close channel]
    G --> H[End]
    B -- No --> I[Wait for channel to open]
    I --> B

```

