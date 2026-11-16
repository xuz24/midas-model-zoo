"""Cached, optional public GitHub repository enrichment for record pages."""
from collections import OrderedDict
from html import escape
from html.parser import HTMLParser
import os
import re
from threading import Lock
from time import monotonic
from urllib.parse import quote, urljoin, urlsplit

import bleach
import requests

from .records import safe_url

_cache = OrderedDict()
_lock = Lock()


def repository_path(record):
    for key in ('github_url', 'repository_url', 'source_url', 'repo_url', 'github'):
        value = record.get(key)
        if not isinstance(value, str):
            continue
        parsed = urlsplit(value)
        parts = parsed.path.strip('/').split('/')
        if (parsed.scheme in {'http', 'https'} and parsed.netloc.lower() in {'github.com', 'www.github.com'}
                and len(parts) >= 2 and re.fullmatch(r'[A-Za-z0-9-]+', parts[0])):
            repo = parts[1].removesuffix('.git')
            if re.fullmatch(r'[A-Za-z0-9_.-]+', repo) and repo not in {'.', '..'}:
                return f'{parts[0]}/{repo}'
    return None


class _ReadmeLinks(HTMLParser):
    def __init__(self, base, raw):
        super().__init__(convert_charrefs=False)
        self.base, self.raw, self.output = base, raw, []

    def handle_starttag(self, tag, attrs):
        result = []
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                if not value.startswith('#'):
                    value = urljoin(self.raw if key == 'src' else self.base, value)
                if not value.startswith('#') and not safe_url(value):
                    continue
            result.append(f' {key}="{escape(value or "", quote=True)}"')
        self.output.append(f'<{tag}{"".join(result)}>')

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')


def _readme_attribute(tag, name, value):
    """Keep README layout hints without allowing arbitrary styles or handlers."""
    if name == 'align':
        allowed = {'left', 'center', 'right', 'justify'} if tag in {'p', 'div', 'th', 'td'} else {'left', 'right', 'top', 'middle', 'bottom'}
        return tag in {'p', 'div', 'th', 'td', 'img'} and value.lower() in allowed
    if tag == 'img' and name in {'width', 'height'}:
        # HTML dimensions are positive pixel counts; percentage widths are also
        # common in READMEs. Never accept CSS expressions or other units here.
        if re.fullmatch(r'[1-9][0-9]{0,5}', value):
            return True
        return name == 'width' and bool(re.fullmatch(r'(?:[1-9][0-9]?|100)%', value))
    return name in {'a': {'href', 'title', 'id'}, 'img': {'src', 'alt', 'title'}}.get(tag, set())


def sanitize_readme(html, path, branch):
    clean = bleach.clean(html, tags={'a', 'p', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'strong', 'em', 'del', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'details', 'summary', 'div', 'span'},
        attributes=_readme_attribute, protocols={'http', 'https'}, strip=True)
    ref = quote(branch, safe='')
    parser = _ReadmeLinks(f'https://github.com/{path}/blob/{ref}/',
                          f'https://raw.githubusercontent.com/{path}/{ref}/')
    parser.feed(clean)
    return ''.join(parser.output)


def fetch_repository(path):
    """Cache successes for 15 minutes and failures for one minute; bound memory."""
    now = monotonic()
    with _lock:
        cached = _cache.get(path)
        if cached and cached[0] > now:
            return cached[1]
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'Michigan-Research-Hub',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    result = None
    try:
        response = requests.get(f'https://api.github.com/repos/{path}', headers=headers,
                                timeout=(2, 5), allow_redirects=False)
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError('Unexpected GitHub response')
        data = response.json()
        result = {key: data.get(key) for key in ('full_name', 'description', 'stargazers_count',
            'forks_count', 'language', 'created_at', 'updated_at', 'topics')}
        result.update(url=f'https://github.com/{path}', homepage=safe_url(data.get('homepage')),
                      license=(data.get('license') or {}).get('name'), readme=None)
        try:
            readme = requests.get(f'https://api.github.com/repos/{path}/readme',
                headers={**headers, 'Accept': 'application/vnd.github.html+json'},
                timeout=(2, 5), allow_redirects=False)
            if readme.status_code == 200:
                result['readme'] = sanitize_readme(readme.text, path, data.get('default_branch') or 'HEAD')
        except requests.RequestException:
            pass
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        result = None
    with _lock:
        _cache[path] = (monotonic() + (900 if result else 60), result)
        _cache.move_to_end(path)
        while len(_cache) > 256:
            _cache.popitem(last=False)
    return result
