---
title: "Notebooks for Scripting"
date: 2024-12-30T00:00:00+03:00
tags: ['personal', 'en', 'shell', 'python']
draft: true
---

Did you know that
```python {lineNos=table tabWidth=4 style=emacs}
files = !ls *.ipynb
for index, file in enumerate(files):
    print(f"[{index}] {file}")
```

works and outputs as one could only dream:
> [0] analysis.ipynb  
[1] imaginary.ipynb

It is real; IT JUST WORKS!
