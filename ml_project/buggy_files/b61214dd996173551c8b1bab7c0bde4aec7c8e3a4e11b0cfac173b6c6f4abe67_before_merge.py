    def names(self) -> List[str]:
        """
        Names of determined scales.

        Returns:
            List[str]: list of names
        """
        if self.method == "standard":
            return ["mean", "scale"]
        else:
            return ["median", "scale"]