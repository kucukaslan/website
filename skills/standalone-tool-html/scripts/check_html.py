#!/usr/bin/env python3
"""Check the static HTML contract; this is not a browser or security audit."""
import argparse
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

THEME = re.compile(r'<!-- standalone-theme:start -->.*?<!-- standalone-theme:end -->', re.S)
DESCRIPTION = re.compile(r'''<meta\s+name=["']description["']\s+content=["']([^"']+)["']\s*/?>''', re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = Counter()
        self.ids = []
        self.lang = ''
        self.descriptions = []
        self.viewport = False
        self.theme_options = set()
        self.in_theme_select = False
        self.body_classes = []
        self.resources = []
        self.css = []
        self.in_style = False
        self.text_tag = None
        self.text = {'title': '', 'h1': ''}

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        self.tags[tag] += 1
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'body':
            self.body_classes = a.get('class', '').split()
        if tag == 'meta' and a.get('name', '').lower() == 'description':
            self.descriptions.append(a.get('content', '').strip())
        if tag == 'meta' and a.get('name', '').lower() == 'viewport':
            self.viewport = 'width=device-width' in a.get('content', '').replace(' ', '').lower()
        if tag == 'select' and a.get('id') == 'tool-theme':
            self.in_theme_select = True
        if tag == 'option' and self.in_theme_select:
            self.theme_options.add(a.get('value'))
        for attr in ('src', 'poster'):
            if a.get(attr):
                self.resources.append(a[attr])
        if tag == 'link' and a.get('href'):
            self.resources.append(a['href'])
        if tag == 'object' and a.get('data'):
            self.resources.append(a['data'])
        if a.get('srcset'):
            # The starter needs no srcset. Avoid guessing how data URLs split.
            self.resources.append('unreviewed-srcset:' + a['srcset'])
        if a.get('style'):
            self.css.append(a['style'])
        if tag == 'style':
            self.in_style = True
        if tag in self.text:
            self.text_tag = tag

    def handle_endtag(self, tag):
        if tag == 'select':
            self.in_theme_select = False
        if tag == 'style':
            self.in_style = False
        if tag == self.text_tag:
            self.text_tag = None

    def handle_data(self, data):
        if self.in_style:
            self.css.append(data)
        if self.text_tag:
            self.text[self.text_tag] += data


def check(path, offline=False):
    source = path.read_text(encoding='utf-8')
    page = Page()
    page.feed(source)
    errors = []
    if not re.match(r'\s*<!doctype\s+html\s*>', source, re.I):
        errors.append('Start with <!doctype html>.')
    for tag in ('html', 'head', 'body', 'title', 'h1'):
        if page.tags[tag] != 1:
            errors.append(f'Expected one {tag} element, found {page.tags[tag]}.')
    if not page.lang:
        errors.append('Set the document language.')
    early_source = source.encode('utf-8')[:1024].decode('utf-8', errors='ignore')
    if not re.search(r'''<meta\s+charset=["']utf-8["']\s*/?>''', early_source, re.I):
        errors.append('Declare UTF-8 within the first 1024 bytes.')
    if not page.viewport:
        errors.append('Include a width=device-width viewport meta tag.')
    if not all(text.strip() for text in page.text.values()):
        errors.append('Use a nonempty title and h1.')
    if len(page.descriptions) != 1 or not all(page.descriptions) or len(DESCRIPTION.findall(source)) != 1:
        errors.append('Use one catalog-compatible description: name then content; escape quotes within content.')
    duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
    if duplicates:
        errors.append('Duplicate IDs: ' + ', '.join(duplicates))
    if not {'tool-theme', 'tool-content'}.issubset(page.ids) or 'tool-page' not in page.body_classes:
        errors.append('Preserve tool-theme, tool-content, and the tool-page body class.')
    if page.theme_options != {'system', 'light', 'dark'}:
        errors.append('Preserve system, light, and dark theme option values.')
    baseline = Path(__file__).resolve().parents[1] / 'assets/starter.html'
    if THEME.findall(source) != THEME.findall(baseline.read_text()):
        errors.append('Embed the unmodified shared theme from assets/starter.html.')
    if re.search(r'__TOOL_[A-Z_]+__', source):
        errors.append('Replace all starter tokens and implement the actual tool.')
    css = '\n'.join(page.css)
    page.resources.extend(re.findall(r'''url\(\s*["']?([^\s"')]+)''', css, re.I))
    page.resources.extend(re.findall(r'''@import\s+["']([^"']+)''', css, re.I))
    remote = []
    for resource in sorted(set(page.resources)):
        if resource.startswith(('data:', '#')):
            continue
        parsed = urlsplit(resource)
        if parsed.scheme == 'https' and parsed.netloc:
            remote.append(resource)
        else:
            errors.append('Embed or review this non-HTTPS resource: ' + resource)
    if offline and remote:
        errors.append('Offline mode forbids external runtime resources.')
    return errors, remote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--offline', action='store_true', help='Reject declared external resources')
    args = parser.parse_args()
    errors, remote = check(args.html, args.offline)
    for error in errors:
        print('FAIL: ' + error)
    for url in remote:
        print('ONLINE RESOURCE: ' + url)
    if errors:
        raise SystemExit(1)
    print('Static HTML contract passed. Runtime behavior and dynamically created resources still need review.')


if __name__ == '__main__':
    main()
