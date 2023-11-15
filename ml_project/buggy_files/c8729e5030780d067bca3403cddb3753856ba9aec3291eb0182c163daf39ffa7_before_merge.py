    def _find_url(self, known_keys: set, links: dict) -> str:
        intersection = known_keys.intersection(links)
        iterator = iter(intersection)
        key = next(iterator, None)
        return links.get(key, {}).get('href', None)