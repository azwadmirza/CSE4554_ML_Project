    def __enter__(self):
        """
        Entering a stage context will create the stage directory

        Returns:
            self
        """
        self.create()
        return self