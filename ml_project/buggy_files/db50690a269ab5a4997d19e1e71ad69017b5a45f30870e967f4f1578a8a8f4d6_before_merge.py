    def _stats(self, a):
        sv = special.errprint(0)
        fac = asarray(special.zeta(a,1))
        mu = special.zeta(a-1.0,1)/fac
        mu2p = special.zeta(a-2.0,1)/fac
        var = mu2p - mu*mu
        mu3p = special.zeta(a-3.0,1)/fac
        mu3 = mu3p - 3*mu*mu2p + 2*mu**3
        g1 = mu3 / asarray(var**1.5)

        mu4p = special.zeta(a-4.0,1)/fac
        sv = special.errprint(sv)
        mu4 = mu4p - 4*mu3p*mu + 6*mu2p*mu*mu - 3*mu**4
        g2 = mu4 / asarray(var**2) - 3.0
        return mu, var, g1, g2