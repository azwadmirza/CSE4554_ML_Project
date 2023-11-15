    def _find_url(self, known_keys: list, links: dict) -> str:
        links_keys = links.keys()
        common_keys = [item for item in links_keys if item in known_keys]
        key = next(iter(common_keys), None)
        return links.get(key, {}).get('href', None)