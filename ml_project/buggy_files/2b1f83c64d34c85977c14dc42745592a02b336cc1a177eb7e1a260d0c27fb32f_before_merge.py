    def jac_mag(self):
        """Magniture of Jacobian of objective function at current iteration."""
        if self._g_mag is None:
            self._g_mag = scipy.linalg.norm(self.jac)
        return self._g_mag