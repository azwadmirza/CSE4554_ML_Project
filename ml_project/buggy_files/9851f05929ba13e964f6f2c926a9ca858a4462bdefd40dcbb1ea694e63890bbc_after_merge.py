def sitemap_urls_from_robots(robots_text, base_url=None):
    """Return an iterator over all sitemap urls contained in the given
    robots.txt file
    """
    for line in robots_text.splitlines():
        if line.lstrip().lower().startswith('sitemap:'):
            url = line.split(':', 1)[1].strip()
            yield urljoin(base_url, url)