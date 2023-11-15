    def is_hash_allowed(self, hashes):
        # type: (Hashes) -> bool
        """
        Return True if the link has a hash and it is allowed.
        """
        if not self.has_hash:
            return False
        # Assert non-None so mypy knows self.hash_name and self.hash are str.
        assert self.hash_name is not None
        assert self.hash is not None

        return hashes.is_hash_allowed(self.hash_name, hex_digest=self.hash)