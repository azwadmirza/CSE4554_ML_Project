    def _update_index(self, url=None):
        """A helper function that ensures that self._index is
        up-to-date.  If the index is older than self.INDEX_TIMEOUT,
        then download it again."""
        # Check if the index is aleady up-to-date.  If so, do nothing.
        if not (self._index is None or url is not None or
                time.time()-self._index_timestamp > self.INDEX_TIMEOUT):
            return

        # If a URL was specified, then update our URL.
        self._url = url or self._url

        # Download the index file.
        self._index = nltk.internals.ElementWrapper(
            ElementTree.parse(compat.urlopen(self._url)).getroot())
        self._index_timestamp = time.time()

        # Build a dictionary of packages.
        packages = [Package.fromxml(p) for p in
                    self._index.findall('packages/package')]
        self._packages = dict((p.id, p) for p in packages)

        # Build a dictionary of collections.
        collections = [Collection.fromxml(c) for c in
                       self._index.findall('collections/collection')]
        self._collections = dict((c.id, c) for c in collections)

        # Replace identifiers with actual children in collection.children.
        for collection in self._collections.values():
            for i, child_id in enumerate(collection.children):
                if child_id in self._packages:
                    collection.children[i] = self._packages[child_id]
                if child_id in self._collections:
                    collection.children[i] = self._collections[child_id]

        # Fill in collection.packages for each collection.
        for collection in self._collections.values():
            packages = {}
            queue = [collection]
            for child in queue:
                if isinstance(child, Collection):
                    queue.extend(child.children)
                else:
                    packages[child.id] = child
            collection.packages = packages.values()

        # Flush the status cache
        self._status_cache.clear()