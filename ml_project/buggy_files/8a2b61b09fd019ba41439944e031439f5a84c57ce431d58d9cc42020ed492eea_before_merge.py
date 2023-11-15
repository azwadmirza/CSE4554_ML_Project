    def changed(self, path_info, hash_info):
        """Checks if data has changed.

        A file is considered changed if:
            - It doesn't exist on the working directory (was unlinked)
            - Hash value is not computed (saving a new file)
            - The hash value stored is different from the given one
            - There's no file in the cache

        Args:
            path_info: dict with path information.
            hash: expected hash value for this data.

        Returns:
            bool: True if data has changed, False otherwise.
        """

        logger.debug(
            "checking if '%s'('%s') has changed.", path_info, hash_info
        )

        if not self.tree.exists(path_info):
            logger.debug("'%s' doesn't exist.", path_info)
            return True

        hash_ = hash_info.get(self.tree.PARAM_CHECKSUM)
        if hash_ is None:
            logger.debug("hash value for '%s' is missing.", path_info)
            return True

        if self.changed_cache(hash_):
            logger.debug("cache for '%s'('%s') has changed.", path_info, hash_)
            return True

        typ, actual = self.tree.get_hash(path_info)
        assert typ == self.tree.PARAM_CHECKSUM

        if hash_ != actual:
            logger.debug(
                "hash value '%s' for '%s' has changed (actual '%s').",
                hash_,
                actual,
                path_info,
            )
            return True

        logger.debug("'%s' hasn't changed.", path_info)
        return False