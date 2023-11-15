    def timezone(self):
        """Get the timezone."""
        return self.send("get_timezone")[0]