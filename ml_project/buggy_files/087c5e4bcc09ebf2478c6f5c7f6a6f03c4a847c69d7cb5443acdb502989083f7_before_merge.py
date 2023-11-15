    def changed_cache_file(self, hash_):
        """Compare the given hash with the (corresponding) actual one.

        - Use `State` as a cache for computed hashes
            + The entries are invalidated by taking into account the following:
                * mtime
                * inode
                * size
                * hash

        - Remove the file from cache if it doesn't match the actual hash
        """
        # Prefer string path over PathInfo when possible due to performance
        cache_info = self.hash_to_path(hash_)
        if self.tree.is_protected(cache_info):
            logger.debug(
                "Assuming '%s' is unchanged since it is read-only", cache_info
            )
            return False

        _, actual = self.tree.get_hash(cache_info)

        logger.debug(
            "cache '%s' expected '%s' actual '%s'", cache_info, hash_, actual,
        )

        if not hash_ or not actual:
            return True

        if actual.split(".")[0] == hash_.split(".")[0]:
            # making cache file read-only so we don't need to check it
            # next time
            self.tree.protect(cache_info)
            return False

        if self.tree.exists(cache_info):
            logger.warning("corrupted cache file '%s'.", cache_info)
            self.tree.remove(cache_info)

        return True