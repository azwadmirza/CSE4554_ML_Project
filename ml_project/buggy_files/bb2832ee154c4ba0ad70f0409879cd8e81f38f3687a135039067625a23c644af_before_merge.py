    def redirect(self, location, status=302, lock=0):
        """Cause a redirection without raising an error"""
        if isinstance(location, HTTPRedirection):
            status = location.getStatus()
        location = str(location)
        self.setStatus(status, lock=lock)
        self.setHeader('Location', location)
        return location