    def triples(self) -> np.ndarray:  # noqa: D401
        """The labeled triples."""
        # TODO: Deprecation warning. Will be replaced by re-constructing them from ID-based + mapping soon.
        return self._triples