#!/usr/bin/env python3
"""Embed shared theme sources; the resulting HTML needs no build or local assets."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- standalone-theme:start -->'
END = '<!-- standalone-theme:end -->'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if embedded themes are stale')
    args = parser.parse_args()
    css = (ROOT / 'assets/css/standalone-tools.css').read_text().rstrip()
    js = (ROOT / 'assets/js/standalone-tools.js').read_text().rstrip()
    block = f'{START}\n<style>\n{css}\n</style>\n<script>\n{js}\n</script>\n{END}'
    stale = []
    for path in sorted((ROOT / 'static/tools').glob('*.html')):
        source = path.read_text()
        if START in source:
            if source.count(START) != 1 or source.count(END) != 1:
                raise ValueError(f'Invalid theme markers in {path}')
            updated = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, source, count=1, flags=re.S)
        else:
            updated, count = re.subn(r'(?i)(<meta\s+charset=[^>]+>)', lambda m: m[0] + '\n' + block, source, count=1)
            if not count:
                raise ValueError(f'Missing charset declaration in {path}')
        if source != updated:
            stale.append(path.name)
            if not args.check:
                path.write_text(updated)
    if args.check and stale:
        parser.exit(1, 'Stale standalone themes: ' + ', '.join(stale) + '\n')
    print('Themes are current.' if args.check else f'Updated {len(stale)} standalone themes.')


if __name__ == '__main__':
    main()
