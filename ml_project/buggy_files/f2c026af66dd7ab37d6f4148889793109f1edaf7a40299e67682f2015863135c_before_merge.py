    def array_interface(self):
        """Provide the Numpy array protocol."""
        return self.coords.array_interface()