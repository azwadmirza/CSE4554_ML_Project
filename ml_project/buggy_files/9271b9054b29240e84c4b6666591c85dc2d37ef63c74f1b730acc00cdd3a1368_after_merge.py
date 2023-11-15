    def _stats(self, c):
        c2 = c*c
        mu = c2 / 2.0 + 1
        den = 5*c2 + 4
        mu2 = c2*den / 4.0
        g1 = 4*c*sqrt(11*c2+6.0)/np.power(den, 1.5)
        g2 = 6*c2*(93*c2+41.0) / den**2.0
        return mu, mu2, g1, g2