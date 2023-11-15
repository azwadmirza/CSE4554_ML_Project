    def __lt__(self, other):
        """Less than."""
        """Compare DatasetIDs with special handling of `None` values"""
        # modifiers should never be None when sorted, should be tuples
        if isinstance(other, DatasetID):
            other = other._comparable()
        return super(DatasetID, self._comparable()).__lt__(other)