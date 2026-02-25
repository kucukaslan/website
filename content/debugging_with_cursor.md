---
title: "Fixing 9 Years Old OSS Bug with Cursor"
date: 2026-02-25T12:00:00+03:00
draft: false
tags: ['English', 'cursor', 'osmium']
---

> Last things first: this is the revisionist history of a [PR fixing a few years old bug in osmium-tool](https://github.com/osmcode/osmium-tool/pull/305), an opensource tool for working with OpenStreetMap (OSM) data.

> First things second: [osmium](https://github.com/osmcode/osmium-tool) is one of my favourite tools when I work with the OSM data, along with the [JOSM editor](https://josm.openstreetmap.de/). I use osmium-tool for manipulating data, JOSM editor for visualizing and examining the data -ironically never for editing.


## Background and Purpose

We wanted to limit use of ways that are strictly inside in a given region.
A region is defined by one or more [simple polygon](https://en.wikipedia.org/wiki/Simple_polygon)s. 

Ways on the other hand have an obvious common sense definition[^asphalt].
[^asphalt]: Nooo, it ain't the asphalt!

It's a continuous curve where things can move along.
But it's formal definition in the OSM data neither includes all ways nor exludes all non-ways in the the real-world (common sense) conceptualization.

In the OSM, we need to define `node`s first as points (coordinates) in the space with some additional data (i.e. tags).
Then a `way` in OSM is defined as a (finite) sequence of nodes with some additional data (e.g. speed limits, access restrictions).
We can informally call way segment to a portion of the way that connects two consecutive nodes in the wat.

Since a physical way may have different lanes, speed limits etc. OSM splits a single physical way into multiple pieces.

As if this discrepancy wasn't enough, we needed to handle arbitrary regions.
Thus a region may include only a portion of the ways. Even OSM's ways weren't precise enough for our needs.
We could merely tolerate exclusions at way segment precision.

In short we needed to find all way segments inside a given polygon.

## Enter [osmium-tool](https://github.com/osmcode/osmium-tool)
osmium-tool has a feature to _[create a geographical extract](https://osmcode.org/osmium-tool/manual.html#creating-geographic-extracts) of OSM data that only contains the data for a specific region_.
That's exactly what we wanted, right?\
Almost: inclusion of the roads that intersects the region boundary, the nodes on such nodes that are inside or outside the region depends on the use case. 
osmium-tool provides 3 extraction strategies:

### simple
> When using the simple strategy, all nodes inside the specified region are included and all nodes that are outside the region are not included. All ways that have at least one node inside the region are included, but they might be missing some nodes, they are not reference-complete. 

<!-- render the svg image /img/extract-strategy-simple.svg -->
<img src="/img/extract-strategy-simple.svg" alt="Demonstration of simple extraction strategy" />


<details>

<summary> Expand for complete_ways and smart strategies</summary>

### complete_ways
> When using the complete_ways strategy, all nodes inside the specified region as well as all nodes used by ways that are partially inside the specified region will be in the output.
<!-- render the svg image /img/extract-strategy-complete-ways.svg -->
<img src="/img/extract-strategy-complete-ways.svg" alt="Demonstration of complete_ways extraction strategy" />

### smart
When using the smart strategy, everything is done as in the complete_ways strategy, but multipolygon relations that have at least one node in the region will also be completely included.
<!-- render the svg image /img/extract-strategy-smart.svg -->
<img src="/img/extract-strategy-smart.svg" alt="Demonstration of smart extraction strategy" />

</details>

the simple strategy sounds great for our needs.
Beware that it extracts nodes and ways. But we need to find way segments (consecutive node pairs that are part of those ways) inside the region. 
When we extract the region we are interested with simple strategy it will give ways that intersects the region boundary, so some segments of those ways rest outside the region. So we need to filter out those segments by checking if both of their nodes are inside the extraction as well.

## First Draft and Noticing the Problem
It's implementation was pretty straightforward.
Then we started testing it multiple regions on random places.
Areas highlighted in red in the left side are the regions we want to examine/extract.
The points are the nodes and the lines are the way segments. 
Brown segments are all the segments we founded in the regions (other segments are colored in orange, cyan, green etc.):
![osmium-polygon-overlay](/img/osmium-polygon-overlay.png)

Disappointingly, there were non-brown segments inside the region (even if their both nodes were inside the region).
First, I went over my implementation nothing suspicious. It was a straightforward code anyway.
Then I started examining the wrong segments if they have any common thing: same road type, same tags, etc. with [JOSM editor](https://josm.openstreetmap.de/).
In fact, for a specific way whose multiple segments were inside the region, only a single segment was included.[^partial]

[^partial]: In retrospect we understood that this happened because we have two overlapping regions. The way was correctly included for one of them but it was incorrectly excluded for the other one.

I was stuck: there was nothing common for the wrong segments, my code seems to correctly handle edge cases, my logic -obviously- was sound.

I need to check the state at every step to find where the code failed.

## Enter Cursor and Claude Sonnet | Opus
I decided that it was the time I plea to AI overlords!

> Last things first (one more time):
you can find export of Cursor session that I used for debugging and fixing the issue [here](/cursor_map_segment_speed_changes_within).
I will go over the steps below, but you can examine the export for raw interaction.  
Also beware that export does not include the images, file and code references that I added to context. Similarly the interaction with terminal and other tools are not included either.

I initated the chat by sharing the [previous image that shows the error](/img/osmium-polygon-overlay.png). \
Instead of explicitly stating the issue I explained what the colors, lines etc. mean, what my intent was and asked it to evaluate the result. \
By doing so, _I hoped to verify both that it understood my intention and it really examined the image, not just slopping plausibly sounding success/mistakes with a gazillion buzzwords._

It, to my mild surprise it made really a good job. 
It correctly explained my implementation and identified two issues:
> 1. **Some roads inside polygons appear to still be cyan** (normal speed) on the right side
> 2. **Some dark-gray roads seem to extend beyond** the polygon boundaries on the left

well, the second one is incorrect, but I'll look over that.
It presented three reasonable root causes:
> 1. **Boundary segments excluded**: Road segments that cross the polygon edge (one node inside, one outside) are intentionally skipped by your current logic
> 2. **OSM way structure**: Long ways with sparse node density might have few segments fully contained within narrow polygon strips
> 3. **Node position vs line geometry**: A road segment might visually appear inside the polygon, but if either of its endpoint nodes is outside, it won't be affected

It followed with clarifacation questions on what should be done for the boundary segments and what specific issue I want it to fix. My reply was skip boundary segments and fix the unaffected way segment inside the polygons.

It made a plan for reproducing the issue and asked for IDs for the specific ways and nodes.

I prepared an OSM file for the region (so that it won't waste time on processing the a full map), shared IDs of a way segment and corresponding nodes that was clearly inside the red polygons and the polygon coordinates.

It started with sanity checks that the nodes were inside of the polygon.

Then I shared list of way segments that our current implementation found.

It checked whether there was an issues with specific nodes and their neighbours:
> Node 5992278830: lon=30.7155, lat=36.9051 ✓ captured \
Node 36245618: lon=30.7161, lat=36.9051 ✗ NOT captured \
 \
 **CONFIRMED: All 4 nodes are geometrically INSIDE the polygon**, but only 2 were captured:
| Node | lon | lat | Inside Polygon | Captured |
|------|-----|-----|----------------|----------|
| 990339773 | 30.7162 | 36.9046 | ✓ | ✓ |
| 5992278830 | 30.7155 | 36.9051 | ✓ | ✓ |
| 4339961951 | 30.7161 | 36.9057 | ✓ | ✗ |
| 36245618 | 30.7161 | 36.9051 | ✓ | ✗ |
>
>This is a critical finding! The issue is NOT with the polygon geometry or the containment logic. _Something is wrong with the osmium extraction or the PBF file being used_.

I verified that PBF file was correct. But it suspected that our polygon coordinates were counter-clockwise against the [RFC 7946 Specs](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.6) to no avail.

It made a plan to use custom node and way extraction logic instead, but I stopped it and asked it to focus on reproducing the issue.

After implementing and running the reproduction code it found:
>**Surprising result!** osmium correctly extracts ALL 4 nodes from `debug.osm.pbf`! \
This means the issue is NOT with osmium. Let me now trace the full segment generation to find where the segments are being lost: \
**Found the issue!** Way 91747534 is NOT in the filtered PBF! \
The nodes (36245618, 5992278830) ARE inside the polygon, but the WAY that contains them is missing... so osmium's "simple" strategy should include it, but **it's NOT in the filtered output!** \
This is an osmium bug or edge case. Let me compare with ways that ARE included:

It continued thinking and running reproduction and finally come with a strong hypothesis:
> **Major discovery!** osmium is missing **28 ways** that should be included!
>
> Let me check if there's a pattern - maybe osmium is only including ways that START inside the polygon:
>
> **ROOT CAUSE FOUND!**
> 
> | Category | Count |
> |----------|-------|
> | INCLUDED ways with first node INSIDE | 83 |
> | INCLUDED ways with first node OUTSIDE | 0 |
> | MISSING ways with first node INSIDE | 0 |
> | MISSING ways with first node OUTSIDE | 28 |
> 
> **osmium's "simple" strategy only includes ways where the FIRST node is inside the polygon!** Ways that start outside but enter the polygon are incorrectly skipped!

At this point it started coming with a workaround by using custom filters on top of other extraction methods. \
However, its hypothesis excited me and I wanted to find the root cause. I had previously cloned the osmium-tool repository for potentially adding a new extraction method that fits our other uses cases but didn't complete since I couldn't how it should handle some cases that were irrelevant to our use case but could be relevant to other people using the osmium-tool. \
Anyway, due to this previous exposure I knew where exactly to look for the issue: [src/extract/strategy_simple.cpp](https://github.com/osmcode/osmium-tool/blob/v1.18.0/src/extract/strategy_simple.cpp).

I hope, at this point you're no longer naive enough to think that I, myself, read the code. I asked it to examine the code aaaand BINGO:
> Looking at the osmium-tool source code, I found **the bug**!
> 
> ```75:83:osmium-tool/src/extract/strategy_simple.cpp
>         void eway(extract_data* e, const osmium::Way& way) {
>             for (const auto& nr : way.nodes()) {
>                 if (e->node_ids.get(nr.positive_ref())) {
>                     e->write(way);
>                     e->way_ids.set(way.positive_id());
>                 }
>                 return;
>             }
>         }
> ```
> 
> **The `return;` on line 81 is OUTSIDE the `if` block but INSIDE the `for` > loop!**
> 
> This means:
> 1. It checks **only the FIRST node** of the way
> 2. If the first node is inside → write the way
> 3. Then it **immediately returns** without checking any other nodes!
> 
> The correct code should be:
> 
> ```cpp
> void eway(extract_data* e, const osmium::Way& way) {
>     for (const auto& nr : way.nodes()) {
>         if (e->node_ids.get(nr.positive_ref())) {
>             e->write(way);
>             e->way_ids.set(way.positive_id());
>             return;  // <-- Should be INSIDE the if block!
>         }
>     }
> }
> ```

I asked it to fix the code and prepare minimal reproducible test case.

It completed the implementation and prepared the test cases. Then went on setting up C++ environment and running the tests.

I examined the tests, verifyed the test would've failed without the fix and asked a few follow-up questions etc. It really did a great job.\
Right away I commited the changes to my fork and opened a [PR](https://github.com/osmcode/osmium-tool/pull/305) to the upstream repository. \
Two of the CI checks failed, but I verified that they were not related to the changes and informed the maintainers.
A few days later the PR was merged, and the fix was included in the next [release](https://github.com/osmcode/osmium-tool/releases/tag/v1.19.0).


## Conclusion and Reflections
I guess we all have heard how Cursor/LLMs helps non-technical people to create apps, quickly spin up beautiful landing pages, writing compilers etc.\
These are certainly impressive use cases of Cursor and I believe they received, arguably, deserved hype for it.\
However, when I reflect on how Cursor helped solving this issue, I can't help but noticing that, in this particular case, the Cursor did not bring any extra technical expertize. I already knew:
* how it should use the osmium-tool as my original code was accurate (assuming osmium-tool conforms the specs/documentation)
* how can it reproduce the issue as I identified the issue, found problematic node and ways, prepared OSM file for the relevant region
* where the actual implementation of the osmium's extraction was as I found and gave the corresponding file to Cursor. \

On one hand Cursor did not help me debug a problem that I couldn't already debug.\
On the other hand, without Cursor I would not have gone this much way for an issue that I could workaround by writing my own extraction logic and call it a day.\
In this case the problem would be solved as far as I was concerned, but I would neither learn what the actual root cause was nor fix it for all the people using osmium-tool. A missed learning opportunity for me and wasted hours or buggy software for the users. 
Cursor helped to come up with hypothesis on what went wrong, quickly test the hypothesis and iterate until we found the problem in a reasonable with a reasonable cost, in other words Cursor made it feasible to debug the issue until we found the root cause and fix it.\
In addition to debugging it makes many more things feasible.
I have prepared many dashboards that gave us precious insights on the quality of our data analysis results which helped us identify a major bug, that helped us to easily visualize how our customizations affects our route planning.\
I have used it to create custom tools that saved me a lot of time: creating test data, [a visualizer to decode/encode Teltonika's Communication Protocol binary data](/html/teltonika_codec_8_8ext.html).\
These tools gives immeasurable quality of life during development and debugging.\
Efforts required to create them were not usually justified unless they were to be used for really long time by a lot of people.
But, since we can have the LLMs prepare them in a few prompts with a little bit of guidance,
I can write quick scripts, jupyter notebooks for my own specific needs.\
I really appreciate how these simple things my life easier and my code better, this post was a means to show my appreciation.
