---
title: 'Reflections on AI Proofs: Simple but Hard over Easy but Complex'
date: 2026-11-23T00:00:00+03:00
draft: false
tags: ['reflections', 'mathematics', 'AI', 'computers', "proof"]
language: en
content_type: opinion
# series: ['series-name']
---

There are two main axes by which to evaluate the difficulty ([un]solvability) of a problem: first one is **simple–complex** and the other one is **easy–hard**.

These axes correlate strongly, but neither necessarily independent of nor related to each other.

The easy–hard axis, on the other hand, is usually related to how much work/effort is required to achieve something. This usually includes (human-)time and memory (keeping things in mind, remembering),

Calculating 
`3 + 3`
is both simple and easy.

What if we encounter a problem that isn't quite as easy and simple? Let's say adding 3 for 1260 times.

<!--Calculating `3 + 3 + 3 + ... + 3` is still simple, but a little bit harder, while calculating `3^100` is more complex, but still easy.-->


<!--One option is to perform-->
The simple option is to make addition operation for 1260[^pedantic] times.

The more complex option is to invent a more complex tool or mechanism to handle this kind of hard problem with ease.

In this case, the invention of multiplication suffices to make the problem sufficiently easy to solve.

When problems became even harder, e.g. calculating `325 × 642` (more like `34278113 × 13478891`), we invented logarithms/exponentials and other mechanisms to make problems easier to solve, at the expense of the complexity of these new tools.

Yes, using logarithms for multiplication was [a thing](https://www.open.edu/openlearn/science-maths-technology/mathematics-statistics/john-napier/content-section-5#:~:text=to%20replace%20the%20wearisome%20task%20of%20multiplying%20two%20numbers%20by%20the%20simpler%20task%20of%20adding%20together%20two%20other%20numbers), infact logarithms was invented exactly for this reason.

<!--### The Previous Paradigm Shift: Computers-->

Computers and calculators themselves were physical machinery that made hard problems easier to solve.

From this point of view, the invention of computers represented a deviation from the methods traditionaly we used to employ to tackle new problems. It was a major paradigm shift.

<!--### The Next Paradigm Shift: AI-->

AI is the next step in of the paradigm shift.

Before AI, we were limited to predefined, deterministic, algorithmic methods for using computers to make hard problems easier.

**AI broke through this limitation.**

Before AI, it was generally accepted that, with our existing tools, a human lifetime wouldn't suffice to solve problems like the Riemann Hypothesis the hard way. We therefore needed to invent more complex tools to make their solutions manageable—less hard.

Before AI, it was given (with the existing tools) that a human lifetime wouldn't suffice to solve problems like the Riemann Hypothesis the hard way. We therefore needed to invent more complex tools/machinery/abstractions to make their solutions manageably less hard.


(modern) Mathematics increasingly became the study of inventing these tools and mechanisms to apply to problems.

Until the AI revolution (or revelations?), proving or disproving these problems was synonymous with inventing new tools and mechanisms.

What made the big mathematical problems worthy of such endeavor wasn't their answers, but their solutions[^not-ai].

<!--### Answers Versus Solutions-->

I do enjoy the jokes made about mathematics. They're all just jokes, though.

Mathematicians' reactions, [including those of Terence Tao](https://mathstodon.xyz/@tao/117395267721642920), are more or less attempts to explain the difference between the value of solutions and the value of answers.

Our incentives belonged to an era where the value of an answer was a very strong indicator of the value of its solution.

Clearly, that era is over.

It's over much earlier than decision-makers anticipated.

<!--### The Implications for Software Engineering-->

As a professional software engineer, I feel the need to acknowledge a similar change in our field.

Most of our best practices belong to a time when coding was hard/time-consuming and expensive.

But that era is undoubtedly over.

The design patterns, code reviews, rule of thumbs like DRY/KISS was more valuable back then.

Now, it is inevitable that **we must go against some of the tenets and conventions we held so highly**.

[^pedantic]: I assume implicit addition operation `0+3` for the first 3 just to piss off pedantic mathematicians
    ```
    total = 0
    for i=0; i < 1260; i++:
      total = total + 3
    ```

[^not-ai]: I literally handwritten the part "wasn't their answers, but their solutions", it is not AI. I can even show the photo of the original draft.
