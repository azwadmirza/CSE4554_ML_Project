    def inbounds(self, index: int) -> bool:
        """
            Is this index >= 0 and < len(self)
        """
        return index >= 0 and index < len(self)