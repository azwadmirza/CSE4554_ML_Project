    def inbounds(self, index: int) -> bool:
        """
            Is this 0 <= index < len(self)
        """
        return 0 <= index < len(self)