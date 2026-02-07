# Map segment speed changes within polygons
_Exported on 12/17/2025 at 09:48:09 GMT+3 from Cursor (2.2.23)_

---

**User**

Examine the image.
I wanted to change the speed of the way segments inside the polygons to 0.1.
On the right you see tiles of an area. dark-gray lines are the ones with speed 0.1.
On the left you see the polygon bans applied on them.
Do you see my intention and can evaluate the result?

---

**Cursor**

Looking at the image, I can see your intention:

1. **Left map**: Shows red/pink polygon overlay areas (the "banned area polygons") 
2. **Right map**: Shows the resulting road network where dark-gray lines represent way segments with speed set to 0.1

**My Observation:**

The dark-gray segments on the right appear to correspond to roads that pass through or intersect with the polygon areas on the left. However, I notice some potential issues:

1. **Some roads inside polygons appear to still be cyan** (normal speed) on the right side
2. **Some dark-gray roads seem to extend beyond** the polygon boundaries on the left

To properly evaluate whether the implementation is working correctly, I need to examine the code that handles this polygon-based speed modification. Let me look at the `osm_processor.py` file you have open:

Now I understand the implementation. Let me examine how the segments are used for speed updates:

```python
# Only include segments where both nodes are inside the polygon
if from_node in valid_nodes and to_node in valid_nodes:
```

Let me check the osmium extract strategy being used:

Now I have a complete understanding of your implementation. Let me evaluate the result:

## Understanding the Implementation

Your code in `osm_processor.py` uses a **conservative approach** for applying speed 0.1 to segments:

1. **osmium extract** with `-s simple` strategy extracts data within the polygon
2. Only **nodes that are physically inside the polygon** are collected in `valid_nodes`
3. **Segment generation** (lines 306-322) only includes segments where **BOTH nodes** are inside the polygon:

```311:316:job/osm_processor.py
        for i in range(len(node_ids) - 1):
            from_node = node_ids[i]
            to_node = node_ids[i + 1]

            # Only include segments where both nodes are inside the polygon
            if from_node in valid_nodes and to_node in valid_nodes:
```

## Evaluation of the Result

**Based on the image:**

| Observation | Status |
|------------|--------|
| Dark-gray lines (speed 0.1) appear within polygon areas | Expected behavior |
| Some roads crossing polygon boundaries remain cyan | Expected - segments straddling boundaries are skipped |
| Some roads inside polygons appear to still be cyan | Potential issue - needs investigation |

**Potential causes for unexpected behavior:**

1. **Boundary segments excluded**: Road segments that cross the polygon edge (one node inside, one outside) are intentionally skipped by your current logic
2. **OSM way structure**: Long ways with sparse node density might have few segments fully contained within narrow polygon strips
3. **Node position vs line geometry**: A road segment might visually appear inside the polygon, but if either of its endpoint nodes is outside, it won't be affected

---

I have a clarifying question to ensure I understand your intent correctly:

```python
        for i in range(len(node_ids) - 1):
            from_node = node_ids[i]
            to_node = node_ids[i + 1]

            # Only include segments where both nodes are inside the polygon
            if from_node in valid_nodes and to_node in valid_nodes:
```

Thank you for clarifying! So the issue is that **some roads that are clearly inside the polygons are still showing as cyan** (normal speed) instead of dark-gray (speed 0.1).

This is likely due to **OSM node sparsity** - a road segment can visually pass through a polygon, but if both of its endpoint nodes happen to be outside the polygon, the segment won't be captured.

Let me investigate the current logic more closely and propose a fix:

```plaintext
     Node A (outside) -----> Node B (inside) -----> Node C (outside)
                            [polygon]
```

```plaintext
     Node A (outside) ----------------> Node B (outside)
                  [polygon is narrow, no nodes inside]
```

Now I understand the root cause. Let me check if we can access node coordinates for a more accurate solution:

Now I have a complete understanding of the issue. Let me create a plan to fix the missing segments problem:

---

**User**

> Segments crossing polygon boundary: included (line intersects polygon)

???

---

**Cursor**

You're right to question that - I contradicted your earlier answer! Let me clarify:

Got it! So you want strict node-based logic:
- Both nodes inside → include
- Any node outside → skip

This is exactly what the current code does. So the question becomes: **why are some segments that appear fully inside the polygon being missed?**

Possible causes:
1. **Osmium extraction boundary precision** - nodes appearing visually inside might be outside at coordinate level
2. **Visualization mismatch** - the polygon overlay on the left vs the tile data on the right might be from different processing runs
3. **Polygon coordinate precision** - small differences between DB geometry and what was processed

Please share the specific location - you can provide:
- **Coordinates** (lon, lat) of a road segment that should be affected but isn't
- **OSM way ID** if you know it
- **Screenshot** with the specific area highlighted
- **Node IDs** from the tile info panel

With a specific example, I can trace through the code logic to identify exactly why that segment is being skipped.

---

**User**

here is the osm file and ids that are incorrectly missed from edge segments:
way 91747534
node 5992278830
node 36245618

@debug.osm (1357-1368) 

I highlighted them with green drawing on the same tile map image

These were the road banning polygons:
```
"POLYGON ((30.71538 36.903661, 30.717053 36.90385, 30.716216 36.899285, 30.714563 36.899457, 30.71538 36.903661))"
"POLYGON ((30.714627 36.909529, 30.714487 36.902268, 30.717836 36.9022, 30.717106 36.909784, 30.714627 36.909529))"
```


---

**Cursor**

```xml
<way id='91747534'>
  <nd ref='1066161581' />
  <nd ref='6178281621' />
  <nd ref='1066161527' />
  <nd ref='1066161550' />
  <nd ref='1066161526' />
  <nd ref='5992278830' />  <!-- This node should be included -->
  <nd ref='36245618' />    <!-- This node should be included -->
</way>
```

Let me examine the `debug.osm` file to find the coordinates of the nodes in question and verify if they're inside the polygons:

I found the node coordinates:
- **Node 36245618**: lon=30.7161436, lat=36.905057
- **Node 5992278830**: lon=30.7154932, lat=36.9050989

Now let me verify if these nodes should be inside Polygon 2:

```
Polygon 2: POLYGON ((30.714627 36.909529, 30.714487 36.902268, 30.717836 36.9022, 30.717106 36.909784, 30.714627 36.909529))

Polygon bounds:
  - lon: 30.7144 to 30.7178
  - lat: 36.9022 to 36.9098

Node 5992278830: lon=30.7155, lat=36.9051 → SHOULD be inside ✓
Node 36245618:   lon=30.7161, lat=36.9051 → SHOULD be inside ✓
```

**Both nodes geometrically ARE inside Polygon 2!** So why are they being missed?

Let me check the polygon file creation to investigate potential issues:

```plaintext
Polygon 2: POLYGON ((30.714627 36.909529, 30.714487 36.902268, 30.717836 36.9022, 30.717106 36.909784, 30.714627 36.909529))

Polygon bounds:
  - lon: 30.7144 to 30.7178
  - lat: 36.9022 to 36.9098

Node 5992278830: lon=30.7155, lat=36.9051 → SHOULD be inside ✓
Node 36245618:   lon=30.7161, lat=36.9051 → SHOULD be inside ✓
```

```python
for lon, lat in polygon_coords:
    f.write(f"    {lon}    {lat}\n")
```

```plaintext
POLYGON ((30.714627 36.909529, 30.714487 36.902268, 30.717836 36.9022, 30.717106 36.909784, 30.714627 36.909529))
```

Let me check how multiple polygons are processed and if there could be an issue with the polygon data flow:

```python
for lon, lat in polygon_coords:
    f.write(f"    {lon}    {lat}\n")
```

I see - both nodes **should geometrically be inside Polygon 2**. Let me investigate the potential causes by checking if there's any coordinate precision or polygon processing issue.

Let me check how the polygons are stored and retrieved:

Based on my analysis:

**The nodes SHOULD be inside Polygon 2:**
- Node 5992278830: (lon=30.7155, lat=36.9051)
- Node 36245618: (lon=30.7161, lat=36.9051)
- Polygon 2 spans: lon 30.7144→30.7178, lat 36.9022→36.9098

Both nodes are geometrically **well inside** the polygon. The current logic should capture them.

**Possible causes for the miss:**

1. **Polygon not processed** - Maybe only Polygon 1 was processed (which has lat max ~36.904, below the nodes at lat ~36.905)
2. **Geometry data mismatch** - The polygon stored in DB differs from what you showed
3. **OSM PBF file issue** - The PBF file used for extraction might have different coordinates for these nodes
4. **osmium extraction edge case** - Some precision issue with the .poly file

**To debug this, I need to verify:**
- Which polygon(s) were actually processed by the job
- What coordinates were written to the .poly file
- Whether osmium extracted these specific node IDs

---

**User**

I already given you the geometry from the DB.
I can give you list of edge segments if necessary.

---

**Cursor**

Yes, please share the edge segments that were created for these polygons (especially Polygon 2). This will show exactly which node pairs were captured vs missed.

If you can share:
1. The edge segments for the polygon that should contain nodes 5992278830 and 36245618
2. Or just confirm: is there **any** edge segment with `from_node=5992278830` or `to_node=5992278830` or similar for node 36245618?

This will tell us if:
- **No segments at all** for these nodes → osmium didn't extract them
- **Some segments exist** but not the specific pair → segment generation logic issue

---

**User**

I saced segments for 694149c0345bafbade608b30 in @maps-service-osrm-updater/active_edge_segments.csv  file

---

**Cursor**

Interesting! I found:
- **5992278830 ↔ 5992278828** exists (both directions)
- **5992278830 ↔ 36245618** is **MISSING**!

Let me verify that node 36245618 has no segments at all:

```plaintext
POLYGON ((30.714627 36.909529, 30.714487 36.902268, 30.717836 36.9022, 30.717106 36.909784, 30.714627 36.909529))
```

**Key finding: Node 36245618 has ZERO edge segments!**

This confirms:
- Node **5992278830** was extracted by osmium (it has segments with neighbor 5992278828)
- Node **36245618** was **NOT extracted** by osmium (no segments at all)

But both nodes should be inside Polygon 2 based on coordinates:
- Node 5992278830: lon=30.7155, lat=36.9051 ✓ captured
- Node 36245618: lon=30.7161, lat=36.9051 ✗ **NOT captured**

Let me check the CSV structure and verify the polygon ID:

Let me check if there are multiple polygon IDs in the CSV - you mentioned two polygon WKTs:

There's only **one polygon_id** (694149c0345bafbade608b30) with 900 segments in the CSV.

But you showed me **two** polygon WKTs:
1. `POLYGON ((30.71538 36.903661, ...))` - lat range: 36.899 to 36.904
2. `POLYGON ((30.714627 36.909529, ...))` - lat range: 36.902 to 36.910

The nodes in question (5992278830 and 36245618) are at lat ~36.905, which is:
- **OUTSIDE Polygon 1** (max lat is 36.904)
- **INSIDE Polygon 2** (lat range 36.902-36.910)

**Critical question:** Does polygon_id `694149c0345bafbade608b30` correspond to Polygon 1 or Polygon 2?

If it's Polygon 1, then the nodes at lat ~36.905 are correctly outside that polygon, and Polygon 2 must have a **different polygon_id** that needs to be checked separately.

So polygon_id `694149c0345bafbade608b30` = Polygon 2 (lat 36.902-36.910).

This confirms the bug: **Node 36245618 at (lon=30.7161, lat=36.9051) SHOULD be inside Polygon 2 but wasn't extracted by osmium.**

Let me check the node definition in the debug.osm file more closely:

I see the node definition:
```
<node id='36245618' lat='36.905057' lon='30.7161436' />
```

**Both nodes should be inside Polygon 2:**
- Node 5992278830: lon=30.7155, lat=36.9051 ✓ captured
- Node 36245618: lon=30.7161, lat=36.9051 ✗ NOT captured

They're at nearly identical latitudes, just 0.0006° apart in longitude. This is very suspicious.

Let me create a quick test to verify if osmium is correctly extracting this node. Can you run this manual test?

```plaintext
<node id='36245618' lat='36.905057' lon='30.7161436' />
```

```plaintext
polygon
1
    30.714627    36.909529
    30.714487    36.902268
    30.717836    36.9022
    30.717106    36.909784
    30.714627    36.909529
END
END
```

```python
        # Close ring by repeating first coordinate if not already closed
        if polygon_coords and polygon_coords[0] != polygon_coords[-1]:
            lon, lat = polygon_coords[0]
            f.write(f"    {lon}    {lat}\n")
```

```plaintext
1    30.714627    36.909529
    30.714487    36.902268
    30.717836    36.9022
    30.717106    36.909784
    30.714627    36.909529
END
END, I think I see a potential issue! The .poly format expects coordinates to be in a SPECIFIC winding order. According to the osmium documentation:> The polygon must be given in the counter-clockwise direction.Let me check if the polygon is counter-clockwise...

Actually, for the .poly format used by osmium, the exterior ring should go counter-clockwise (CCW). Let me verify:Starting at (30.714627, 36.909529):1. 

→ (30.714487, 36.902268): moving left-down (decreasing lon, decreasing lat)2. → (30.717836, 36.9022): moving right (increasing lon, slight decrease in lat)3. → (30.717106, 36.909784): moving left-up (decreasing lon, increasing lat)4. → (30.714627, 36.909529): moving left-down (decreasing lon, decreasing lat)

In standard coordinates where longitude increases rightward and latitude increases upward, I need to determine if this traces counter-clockwise. The winding order might be the culprit here—if osmium expects CCW but I've provided CW coordinates, it could reject the polygon or behave unexpectedly.

Let me verify by checking which side the interior falls on as I traverse each edge. Walking from (30.714627, 36.909529) toward (30.714487, 36.902268) heads south; the interior should lie to my left, which means eastward (higher longitude). That aligns with an interior around lon 30.716. Moving from (30.714487, 36.902268) to (30.717836, 36.9022) goes east; the interior should be to my left, pointing north (higher latitude), consistent with an interior near lat 36.905. The segment from (30.717836, 36.9022) to (30.717106, 36.909784) travels mostly north with a slight westward component; the interior should be to my left, which is westward.

This confirms counter-clockwise winding, which is correct for an exterior ring. The polygon orientation itself appears sound, so the problem lies elsewhere. I should examine the `geometry_to_coordinates` function to see if the WKB geometry stored in the database differs from the WKT representation shown. Though actually, osmium's point-in-polygon test shouldn't be sensitive to winding order anyway. Perhaps the issue is in how the .poly file gets written, or there's something specific about node 36245618 that's causing the mismatch.

Let me check which ways in the debug.osm file actually contain node 36245618.
```

**Shapely confirms BOTH nodes are inside the polygon!**

This means the issue is somewhere in the osmium extraction process, not the polygon geometry itself.

Let me check if there's something special about way 91747534 or if node 36245618 is referenced by other ways:

Node 36245618 is used in **two ways**:
1. **Way 91747534** (794. Sokak - residential) - 36245618 is the LAST node
2. **Way 221287339** (Kızılırmak Caddesi - primary) - 36245618 is in the middle

Let me check if there are segments for the neighbors of 36245618 in way 221287339:

Node 990339773 has segments, but node 4339961951 doesn't appear. Let me check their coordinates:

Let me verify all three nodes with Shapely:

**CONFIRMED: All 4 nodes are geometrically INSIDE the polygon**, but only 2 were captured:

| Node | lon | lat | Inside Polygon | Captured |
|------|-----|-----|----------------|----------|
| 990339773 | 30.7162 | 36.9046 | ✓ | ✓ |
| 5992278830 | 30.7155 | 36.9051 | ✓ | ✓ |
| 4339961951 | 30.7161 | 36.9057 | ✓ | ✗ |
| 36245618 | 30.7161 | 36.9051 | ✓ | ✗ |

**This is a critical finding!** The issue is NOT with the polygon geometry or the containment logic. Something is wrong with the **osmium extraction** or the **PBF file** being used.

Key question: Is the `debug.osm` file the same data source as the PBF file used for extraction?

```python
for lon, lat in polygon_coords:    f.write(f"    {lon}    {lat}\n")d the geometry_to_coordinates function:
return [[coord[0], coord[1]] for coord in coords]```

The polygon_coords coming from geometry_to_coordinates are in `[lon, lat]` format. And create_polygon_file iterates with `for lon, lat in polygon_coords`, which should correctly unpack as lon=coord[0], lat=coord[1].This seems correct...Let me check if there's something weird happening with the .poly file. Maybe I should test osmium directly with the polygon and PBF file.

Actually, I should ask the user to run osmium extract manually to see what nodes get extracted.
```

Since it's the same PBF file, this is very strange. Let me check if there's an issue with osmium's extraction. 

Can you run this command to extract nodes using the polygon and check if node 36245618 is in the output?

Let me check the extraction function more closely - specifically how the filtered PBF is parsed:

```plaintext
polygon_name
ring_name
    lon lat
    lon lat    ...END


polygon_name2
...END
```

Wait! I just realized something critical:

**The .poly format expects CLOCKWISE winding for exterior rings**, but our polygon is **counter-clockwise**!

Let me verify this is causing the issue:

The winding order doesn't affect Shapely's containment check. Let me investigate precision - perhaps there's a floating-point precision issue when writing the .poly file:

The precision is fine. Let me check one more thing - can you verify what PBF file is being used and whether we can run a direct osmium test?

Actually, let me try a different approach. What if the issue is with osmium's "simple" strategy? Let me check the osmium extract command:

I think I've identified the issue. Let me propose a solution:

**Root Cause Hypothesis:** osmium's "simple" strategy point-in-polygon check might have edge cases or precision differences compared to Shapely, causing some nodes to be incorrectly excluded.

**Solution:** Instead of relying on osmium to determine which nodes are "inside" the polygon, we should:
1. Extract node coordinates from the filtered PBF (`locations=True`)
2. Use Shapely to verify which nodes are actually inside the polygon
3. This ensures consistent containment logic with the same algorithm we used for verification

---

**User**

We can write a script/notebook to reproduce the issue on @debug.osm.pbf file first.

---

**Cursor**

Great idea! Let me create a reproduction script that will:
1. Run osmium extract on the debug.osm.pbf with the polygon
2. Compare osmium's extracted nodes vs Shapely's containment check
3. Show exactly which nodes are missing

**Surprising result!** osmium correctly extracts ALL 4 nodes from `debug.osm.pbf`!

This means the issue is NOT with osmium. Let me now trace the full segment generation to find where the segments are being lost:

**Found the issue!** Way 91747534 is NOT in the filtered PBF!

The nodes (36245618, 5992278830) ARE inside the polygon, but the WAY that contains them is missing. Let me investigate why:

**CRITICAL FINDING!**

Way 91747534 has **2 nodes inside the polygon** (5992278830 and 36245618), so osmium's "simple" strategy should include it, but **it's NOT in the filtered output!**

This is an osmium bug or edge case. Let me compare with ways that ARE included:

**Major discovery!** osmium is missing **28 ways** that should be included!

Let me check if there's a pattern - maybe osmium is only including ways that START inside the polygon:

```plaintext
INCLUDED ways with first node INSIDE: 83
INCLUDED ways with first node OUTSIDE: 0
MISSING ways with first node INSIDE: 0
MISSING ways with first node OUTSIDE: 28
```

**ROOT CAUSE FOUND!**

| Category | Count |
|----------|-------|
| INCLUDED ways with first node INSIDE | 83 |
| INCLUDED ways with first node OUTSIDE | 0 |
| MISSING ways with first node INSIDE | 0 |
| MISSING ways with first node OUTSIDE | 28 |

**osmium's "simple" strategy only includes ways where the FIRST node is inside the polygon!** Ways that start outside but enter the polygon are incorrectly skipped!

Let me try the "smart" strategy to see if it fixes this:

```plaintext
  Missing ways: 28
  Way 91747534 included: ✗ NO

Strategy 'smart':
  Missing ways: 0  Way 91747534 included: ✓ YESStrategy 'complete_ways':
  Missing ways: 0
  Way 91747534 included: ✓ YES fix is simple: change `-s simple` to `-s smart` in the osmium extract command!Now let me verify that with "smart" strategy, all the target segments are correctly generated.
```

**SOLUTION FOUND!**

| Strategy | Ways Included | Missing | Way 91747534 |
|----------|--------------|---------|--------------|
| simple | 83 | 28 | ✗ NO |
| **smart** | 111 | 0 | **✓ YES** |
| complete_ways | 111 | 0 | ✓ YES |

The fix is simple: **change `-s simple` to `-s smart`** in the osmium extract command!

Let me verify the full segment generation works with the "smart" strategy:

**Wait!** There's a problem. With "smart" strategy, ALL nodes of way 91747534 are now in `valid_nodes`, including nodes that are **OUTSIDE** the polygon!

This means segments like `1066161581 -> 6178281621` (both outside the polygon) would be incorrectly included.

Let me verify this is an issue:

**Complete solution verified!**

The fix requires **two changes**:
1. **Use "smart" strategy** for osmium extract (to include ways that start outside)
2. **Use Shapely for node filtering** (to correctly identify nodes inside polygon)

This gives us the correct result:
- Segment `5992278830 -> 36245618`: ✓ INCLUDED (both inside)
- Segments outside: ✗ SKIPPED (correctly)

Let me update the plan:

---

**User**

Can you examine @osmium-tool/src/extract/strategy_simple.cpp 

---

**Cursor**

```cpp
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
        }
        return;  // <-- BUG! This returns after checking ONLY THE FIRST NODE!
    }
}
```

```cpp
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
            return;  // <-- Should be inside the if block
        }
    }
}
```

Looking at the osmium-tool source code, I found **the bug**!

```75:83:osmium-tool/src/extract/strategy_simple.cpp
        void eway(extract_data* e, const osmium::Way& way) {
            for (const auto& nr : way.nodes()) {
                if (e->node_ids.get(nr.positive_ref())) {
                    e->write(way);
                    e->way_ids.set(way.positive_id());
                }
                return;
            }
        }
```

**The `return;` on line 81 is OUTSIDE the `if` block but INSIDE the `for` loop!**

This means:
1. It checks **only the FIRST node** of the way
2. If the first node is inside → write the way
3. Then it **immediately returns** without checking any other nodes!

The correct code should be:

```cpp
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
            return;  // <-- Should be INSIDE the if block!
        }
    }
}
```

**This is a confirmed bug in osmium-tool!** The indentation makes it look correct, but the `return` statement exits after checking only the first node, regardless of whether it's inside the polygon.

This explains exactly what we observed:
- Ways with first node inside: 83 included
- Ways with first node outside: 0 included (all 28 missing)

Would you like to:
1. Report this bug to osmium-tool maintainers?
2. Proceed with our workaround (use "smart" strategy + Shapely filtering)?
3. Both?

```cpp
        void eway(extract_data* e, const osmium::Way& way) {
            for (const auto& nr : way.nodes()) {
                if (e->node_ids.get(nr.positive_ref())) {
                    e->write(way);
                    e->way_ids.set(way.positive_id());
                }
                return;
            }
        }
```

```cpp
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
            return;  // <-- Should be INSIDE the if block!
        }
    }
}
```

---

**User**

Can we fix it? We already have the repo cloned. 
Can we prepare minimal reproducible test as well  @extract 

---

**Cursor**

Yes! Let me examine the existing test structure to create a proper fix and test:

Now I understand the test structure. Let me create a plan for fixing the bug and adding a test:

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

```cpp
/*

Osmium -- OpenStreetMap data manipulation command line tool
https://osmcode.org/osmium-tool/

Copyright (C) 2013-2025  Jochen Topf <jochen@topf.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

*/

#include "strategy_simple.hpp"

#include "../util.hpp"

#include <osmium/handler/check_order.hpp>

#include <cstdlib>
#include <memory>
#include <vector>

namespace strategy_simple {

    Strategy::Strategy(const std::vector<std::unique_ptr<Extract>>& extracts, const osmium::Options& options) {
        m_extracts.reserve(extracts.size());
        for (const auto& extract : extracts) {
            m_extracts.emplace_back(*extract);
        }

        for (const auto& option : options) {
            warning(std::string{"Ignoring unknown option '"} + option.first + "' for 'simple' strategy.\n");
        }
    }

    const char* Strategy::name() const noexcept {
        return "simple";
    }

    class Pass1 : public Pass<Strategy, Pass1> {

        osmium::handler::CheckOrder m_check_order;

    public:

        explicit Pass1(Strategy* strategy) :
            Pass(strategy) {
        }

        void node(const osmium::Node& node) {
            m_check_order.node(node);
        }

        void enode(extract_data* e, const osmium::Node& node) {
            if (e->contains(node.location())) {
                e->write(node);
                e->node_ids.set(node.positive_id());
            }
        }

        void way(const osmium::Way& way) {
            m_check_order.way(way);
        }

        void eway(extract_data* e, const osmium::Way& way) {
            for (const auto& nr : way.nodes()) {
                if (e->node_ids.get(nr.positive_ref())) {
                    e->write(way);
                    e->way_ids.set(way.positive_id());
                    return;
                }
            }
        }

        void relation(const osmium::Relation& relation) {
            m_check_order.relation(relation);
        }

        void erelation(extract_data* e, const osmium::Relation& relation) {
            for (const auto& member : relation.members()) {
                switch (member.type()) {
                    case osmium::item_type::node:
                        if (e->node_ids.get(member.positive_ref())) {
                            e->write(relation);
                        }
                        return;
                    case osmium::item_type::way:
                        if (e->way_ids.get(member.positive_ref())) {
                            e->write(relation);
                        }
                        return;
                    default:
                        break;
                }
            }
        }

    }; // class Pass1

    void Strategy::run(osmium::VerboseOutput& vout, bool display_progress, const osmium::io::File& input_file) {
        vout << "Running 'simple' strategy in one pass...\n";
        const std::size_t file_size = input_file.filename().empty() ? 0 : osmium::file_size(input_file.filename());
        osmium::ProgressBar progress_bar{file_size, display_progress};

        Pass1 pass1{this};
        pass1.run(progress_bar, input_file);

        progress_bar.done();
    }

} // namespace strategy_simple


```

```plaintext
<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" upload="false" generator="testdata">
  <node id="100" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="1" lon="5"/>
  <node id="101" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="2" lon="1"/>
  <node id="102" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="3" lon="1"/>
  <way id="200" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1">
    <nd ref="100"/>
    <nd ref="101"/>
    <nd ref="102"/>
    <tag k="highway" v="residential"/>
  </way>
</osm>

```

```plaintext
<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" upload="false" generator="test">
  <node id="101" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="2" lon="1"/>
  <node id="102" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="3" lon="1"/>
  <way id="200" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1">
    <nd ref="100"/>
    <nd ref="101"/>
    <nd ref="102"/>
    <tag k="highway" v="residential"/>
  </way>
</osm>

```

```cmake
#-----------------------------------------------------------------------------
#
#  CMake Config
#
#  Osmium Tool Tests - extract
#
#-----------------------------------------------------------------------------

function(check_extract _name _input _output _opts)
    check_output(extract ${_name} "extract --generator=test -f osm extract/${_input} ${_opts} -b 0,0,1.5,10" "extract/${_output}")
endfunction()

function(check_extract_cfg _name _input _output _opts)
    check_output(extract cfg_${_name} "extract --generator=test extract/${_input} ${_opts} -c ${CMAKE_CURRENT_SOURCE_DIR}/config.json" "extract/${_output}")
endfunction()

function(check_extract_opl _name _input _output _opts)
    check_output(extract ${_name} "extract --generator=test -f opl extract/${_input} ${_opts}" "extract/${_output}")
endfunction()


#-----------------------------------------------------------------------------

check_extract(clean                input1.osm output-clean.osm "--clean version --clean uid")

check_extract(simple               input1.osm output-simple.osm "-s simple --output-header=xml_josm_upload!")
check_extract(complete_ways        input1.osm output-complete-ways.osm "-s complete_ways")
check_extract(complete_ways_norels input1.osm output-complete-ways-norels.osm "-s complete_ways -S relations=false")
check_extract(smart_default        input1.osm output-smart.osm "-s smart")
check_extract(smart_mp             input1.osm output-smart.osm "-s smart -S types=multipolygon")
check_extract(smart_any            input1.osm output-smart.osm "-s smart -S types=any")
check_extract(smart_nonmp          input1.osm output-smart-nonmp.osm "-s smart -S types=x")

# Test for way that starts outside polygon but has nodes inside (bug fix test)
check_extract(simple_way_starts_outside input-way-starts-outside.osm output-simple-way-starts-outside.osm "-s simple")

check_extract_cfg(simple           input1.osm output-simple.osm "-s simple --output-header=xml_josm_upload=false")

#-----------------------------------------------------------------------------

check_extract(clean64                input64.osm output-clean64.osm "--clean version --clean uid")

check_extract(simple64               input64.osm output-simple64.osm "-s simple --output-header=xml_josm_upload!")
check_extract(complete_ways64        input64.osm output-complete-ways64.osm "-s complete_ways")
check_extract(complete_ways_norels64 input64.osm output-complete-ways-norels64.osm "-s complete_ways -S relations=false")
check_extract(smart_default64        input64.osm output-smart64.osm "-s smart")
check_extract(smart_mp64             input64.osm output-smart64.osm "-s smart -S types=multipolygon")
check_extract(smart_any64            input64.osm output-smart64.osm "-s smart -S types=any")
check_extract(smart_nonmp64          input64.osm output-smart-nonmp64.osm "-s smart -S types=x")

check_extract_cfg(simple64           input64.osm output-simple64.osm "-s simple --output-header=xml_josm_upload=false")

#-----------------------------------------------------------------------------

check_extract_opl(antimeridian-east-bbox antimeridian.opl output-antimeridian-east.opl "--bbox=160,60,180,80")
check_extract_opl(antimeridian-west-bbox antimeridian.opl output-antimeridian-west.opl "--bbox=-180,60,-160,80")
check_extract_opl(antimeridian-east-poly antimeridian.opl output-antimeridian-east.opl "--polygon=extract/polygon-russia-east.geojson")
check_extract_opl(antimeridian-west-poly antimeridian.opl output-antimeridian-west.opl "--polygon=extract/polygon-russia-west.geojson")
check_extract_opl(antimeridian-both-poly antimeridian.opl output-antimeridian-both.opl "--polygon=extract/polygon-russia-all.geojson")
check_extract_opl(antimeridian-reverse-poly antimeridian.opl output-antimeridian-both.opl "--polygon=extract/polygon-russia-reverse.geojson")

check_extract_opl(antimeridian-alaska-east-json w42394837.osm w42394837.opl "--polygon=extract/polygon-us-alaska.geojson")
check_extract_opl(antimeridian-alaska-west-json w46113981.osm w46113981.opl "--polygon=extract/polygon-us-alaska.geojson")
check_extract_opl(antimeridian-alaska-east-poly w42394837.osm w42394837.opl "--polygon=extract/polygon-us-alaska.poly")
check_extract_opl(antimeridian-alaska-west-poly w46113981.osm w46113981.opl "--polygon=extract/polygon-us-alaska.poly")

check_extract_opl(antimeridian-alaska-east-json-no-feature w42394837.osm w42394837.opl "--polygon=extract/polygon-us-alaska-no-feature.geojson")

#-----------------------------------------------------------------------------

```

```plaintext
<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" generator="test">
  <node id="101" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="2" lon="1"/>
  <node id="102" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1" lat="3" lon="1"/>
  <way id="200" version="1" timestamp="2015-01-01T01:00:00Z" uid="1" user="test" changeset="1">
    <nd ref="100"/>
    <nd ref="101"/>
    <nd ref="102"/>
    <tag k="highway" v="residential"/>
  </way>
</osm>

```

Now let me run all existing extract tests to ensure the fix doesn't break anything:

All 31 extract tests pass. Let me mark the final todo as complete:

All tasks completed successfully. Here's a summary:

## Summary of Changes

### 1. Bug Fix in `src/extract/strategy_simple.cpp`

```cpp
// Before (buggy):
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
        }
        return;  // BUG: exits after first node!
    }
}

// After (fixed):
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
            return;  // Now inside if block - exits after finding match
        }
    }
}
```

### 2. New Test Files Created

- **`test/extract/input-way-starts-outside.osm`** - Input file with a way starting outside polygon
- **`test/extract/output-simple-way-starts-outside.osm`** - Expected output showing way is included

### 3. Updated CMakeLists.txt

Added test case:
```cmake
check_extract(simple_way_starts_outside input-way-starts-outside.osm output-simple-way-starts-outside.osm "-s simple")
```

### 4. Test Results

- **31/31 extract tests pass** ✓
- New test verifies the fix works correctly ✓
- Existing tests confirm no regressions ✓

Would you like to create a git commit and/or submit a pull request to the osmium-tool repository?

```cpp
// Before (buggy):
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
        }
        return;  // BUG: exits after first node!
    }
}

// After (fixed):
void eway(extract_data* e, const osmium::Way& way) {
    for (const auto& nr : way.nodes()) {
        if (e->node_ids.get(nr.positive_ref())) {
            e->write(way);
            e->way_ids.set(way.positive_id());
            return;  // Now inside if block - exits after finding match
        }
    }
}
```

```cmake
check_extract(simple_way_starts_outside input-way-starts-outside.osm output-simple-way-starts-outside.osm "-s simple")
```

---

**User**

where is the polygon defined for this test case?

---

**Cursor**

```cmake
function(check_extract _name _input _output _opts)
    check_output(extract ${_name} "extract --generator=test -f osm extract/${_input} ${_opts} -b 0,0,1.5,10" "extract/${_output}")
endfunction()
```

Good question! Looking at the `check_extract` function in CMakeLists.txt:

The polygon is **hardcoded as a bounding box** in the `check_extract` function on line 10:

```cmake
-b 0,0,1.5,10
```

This means: **minlon=0, minlat=0, maxlon=1.5, maxlat=10**

So all tests using `check_extract` use this same bounding box. In my test input file:

| Node | lat | lon | Inside bbox? |
|------|-----|-----|--------------|
| 100 | 1 | **5** | ✗ NO (lon 5 > 1.5) |
| 101 | 2 | 1 | ✓ YES |
| 102 | 3 | 1 | ✓ YES |

The way starts with node 100 (outside), then enters the bbox with nodes 101 and 102. This tests exactly the bug scenario: a way that starts outside but has nodes inside should be included.

```cmake
-b 0,0,1.5,10
```

