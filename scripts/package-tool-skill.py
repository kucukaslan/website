#!/usr/bin/env python3
"""Refresh the portable starter and export a skill ZIP and one-file ChatGPT guide."""
from pathlib import Path
import argparse
import io
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/standalone-tool-html'
OUTPUT = ROOT / 'skill-artifacts'
PATTERN = r'<!-- standalone-theme:start -->.*?<!-- standalone-theme:end -->'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without changing files')
    args = parser.parse_args()
    css = (ROOT / 'assets/css/standalone-tools.css').read_text().rstrip()
    js = (ROOT / 'assets/js/standalone-tools.js').read_text().rstrip()
    block = f'<!-- standalone-theme:start -->\n<style>\n{css}\n</style>\n<script>\n{js}\n</script>\n<!-- standalone-theme:end -->'
    starter_path = SKILL / 'assets/starter.html'
    starter, count = re.subn(PATTERN, lambda _: block, starter_path.read_text(), flags=re.S)
    if count != 1:
        raise ValueError('The starter must contain exactly one shared theme block')
    instructions = (SKILL / 'SKILL.md').read_text()
    body = re.sub(r'^---\n.*?\n---\n', '', instructions, count=1, flags=re.S).strip()
    body = body.replace('[assets/starter.html](assets/starter.html)', 'the complete starter included below')
    body = body.replace('If execution is available, run `python3 scripts/check_html.py OUTPUT.html` relative\nto this skill folder. This checks static portability and catalog compatibility;\nit does not prove runtime behavior or detect every dependency created in JavaScript.\nWithout execution, review the same contract directly.',
                        'Review the portability and catalog contract above. The separate skill ZIP\nincludes an optional Python checker; this single attachment needs no other files.\nUse execution tools for additional checks when they are available.')
    guide = '''# Standalone HTML tools — ChatGPT guide

Attach this file to a conversation and ask:

> Use the attached standalone HTML guide to build [describe the tool]. Return one complete downloadable .html file.

This attachment includes the instructions and full starter source. It does not
require access to a repository, another attachment, or an installed plugin. It is
an explicit guide for the conversation, not an account-wide skill installation.

'''+body+'''

## Complete starter source

Use this source as a starting point. Replace every `__TOOL_*__` token and implement
the requested behavior before returning a finished page. Preserve the shared theme
block exactly; no part of it depends on another file.

```html
'''+starter.rstrip()+'\n```\n'
    outputs = {starter_path: starter.encode(), OUTPUT / 'standalone-tool-html.md': guide.encode()}
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(SKILL.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.name.startswith('.'):
                continue
            # Fixed metadata keeps exports identical until their content changes.
            info = zipfile.ZipInfo(str(Path(SKILL.name) / path.relative_to(SKILL)))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, outputs.get(path, path.read_bytes()))
    outputs[OUTPUT / 'standalone-tool-html.zip'] = archive.getvalue()
    stale = [path for path, data in outputs.items() if not path.exists() or path.read_bytes() != data]
    if args.check and stale:
        parser.exit(1, 'Stale skill exports: ' + ', '.join(str(p.relative_to(ROOT)) for p in stale) + '\n')
    if not args.check:
        for path in stale:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(outputs[path])
    print('Skill exports are current.' if args.check else f'Updated {len(stale)} skill files.')


if __name__ == '__main__':
    main()
