    def __str__(self):
        """Return a human readable version of this message"""
        return f"({type(self).__name__} {(self.obj_id, self.user, self.reason)})"