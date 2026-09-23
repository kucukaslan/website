---
title: "Muhammed Can Küçükaslan"
subtitle: "Senior Backend Engineer"
layout: cv
url: /cv/
description: "Senior backend engineer working on high-traffic Python services, routing systems, and reliable infrastructure."
---

[muhammedcankucukaslan@gmail.com ](mailto:muhammedcankucukaslan@gmail.com ) · [muhammed@kucukaslan.com.tr](mailto:muhammed@kucukaslan.com.tr) · [github.com/kucukaslan](https://github.com/kucukaslan) · [linkedin.com/in/kucukaslan](https://www.linkedin.com/in/kucukaslan/) · [kucukaslan.com.tr](https://kucukaslan.com.tr/)

<!--## Profile

Senior backend engineer building and operating Python services for map-based delivery systems. My work spans APIs, routing and duration estimation, Kubernetes, and production reliability. I also build in Go, Java, and C++, and contribute to open-source tools.-->

## Experience

### Getir — Senior Backend Engineer

*August 2026–present · Map Engine*
- Investigated service memory usages and found Kubernetes requests and limits had been sized around reclaimable filesystem cache. Right-sized relevant deployments; relevant EC2 spend fell by $30 per day, roughly $11k annualized.
- Improved request distribution across Kubernetes pods by tracing how connection pooling fails when used with ClusterIP. After adding a proper L7 routing proxy, most of client timeouts were eliminated and tail latency was shortened: e.g. the share of requests completed under 20 ms rose from 70% to 84%.

### Getir — Backend Engineer II

*February 2025–July 2026 · Map Engine and Field Experience*
- Led IoT integration for vehicle tracking system, building device-specific protocols on scalable Java & Go microservices.
- Owned production Python services for routing and duration estimation, including services handling **350,000+ requests per minute during peak hours**.
- Customized internal OSRM deployments to incorporate historical delivery data and GPS traces using AirFlow, PostgreSQL, and Redis.
- Proactively audited Kubernetes resource limits and HPA policies, achieving a $20,000 reduction in annual infrastructure costs.
- Collaborated on migrating an internal vehicle routing service from Python to C++, doubling performance and saving $10,000+ in monthly recurring costs.
- Deployed infrastructure (Kafka, MongoDB, K8s, EC2) with strict ACL settings using Terraform and Cloud CDKs.
- Migrated CI/CD pipelines from Bitbucket to GitHub Actions.
- Mentored 2+ interns/junior engineers and authored company-wide guides for MongoDB upgrades to improve cross-team knowledge sharing.
- Found and fixed recurring service memory exhaustion issue by tracing it to logging behavior during RabbitMQ maintenance, then changed the shared logging library to spill buffered records to disk under memory pressure.

### Getir — Backend Engineer I

*January 2024–January 2025 · Locals Promo and Field Experience*

- Built and maintained Java/Spring and Go services using Kafka, Redis, and MongoDB, including a courier rewards service. Improved MongoDB query performance and helped reduce database costs by more than $2,000 per month.

### OTO Global — Backend Engineering Intern and Part-time Engineer

*July–November 2023*

- Developed Java/Spring services deployed to Google Cloud Run and Compute Engine; used metrics and logs to diagnose production issues.

### Peak Games — Big Data Platform Engineering Intern

*June–September 2022* · Big Data Platform

- Contributed to [s5cmd](https://github.com/peak/s5cmd), a Go tool for S3 operations. Added [shell completion](https://github.com/peak/s5cmd/pull/500) and [S3 versioning support](https://github.com/peak/s5cmd/pull/475), and [reworked sync](https://github.com/peak/s5cmd/pull/483) to handle directories with millions of files under limited memory.

## Selected public work

- Diagnosed and [fixed a long-standing osmium-tool extraction bug](https://github.com/osmcode/osmium-tool/pull/305); [documented the investigation](https://kucukaslan.com.tr/debugging_with_cursor/).
- Wrote about [Kubernetes connection-level load balancing](https://kucukaslan.com.tr/posts/case_against_clusterip/) and built an [interactive HTTP routing simulator](https://kucukaslan.com.tr/tools/http-routing-simulator.html) to demonstrate the behavior.

## Skills

- **Languages:** Python, Go, Java, C++, SQL. 
- **Backend and data:** FastAPI, Spring, REST APIs, Kafka, Redis, MongoDB, PostgreSQL, OSRM. 
- **Infrastructure:** Kubernetes, Docker, AWS, Google Cloud, Terraform, GitHub Actions, observability and performance analysis.

## Education

**Bilkent University** — B.S. in **Computer Engineering** and B.S. in **Mathematics** (double major), January 2024. **Magna cum laude**; GPAs 3.66/4.00 and 3.65/4.00 respectively.
