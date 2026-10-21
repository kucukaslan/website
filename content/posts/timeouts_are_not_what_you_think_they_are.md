---
title: "AsyncIO Timouts Are Not What You Think They're"
date: 2026-10-21T00:00:00+03:00
tags: ['personal', 'english']
draft: true
url: /template/
---
1. timeout does not necessarily imply that downstream service responded late
```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R1 as A / Request 1
    participant R2 as A / Request 2
    participant B as Service B

    C->>R1: GET /proxy
    C->>R2: GET /block
    R1->>B: HTTP GET (timeout = 500ms)
    Note over R1: Request headers sent, coroutine yields
    activate R2
    Note over R1,R2: t ≈ 0ms — Event loop BLOCKED
    R2->>R2: CPU-bound work (1000ms)
    B-->>R1: 200 OK (t ≈ 20ms)
    Note over R1,B: TCP response available, but A cannot process it
    Note over R1,R2: t = 500ms — Deadline passes, timer cannot execute
    Note over R1,R2: t ≈ 1000ms — Event loop resumes
    deactivate R2
    R2-->>C: 200 OK
    Note over R1: Timeout cancellation processed
    R1-->>C: 504 Timeout (≈ 1001ms)
```

2. there is no definite way for a service to identify whether a specific request it's serving was timed-out by the client.
seriously. (blame the connection reuse)
