    def decomp0(target, eps=1e-15):
        """Decompose target ~Ud(x, y, z) with 0 uses of the basis gate.
        Result Ur has trace:
        :math:`|Tr(Ur.Utarget^dag)| = 4|(cos(x)cos(y)cos(z)+ j sin(x)sin(y)sin(z)|`,
        which is optimal for all targets and bases"""

        U0l = target.K1l.dot(target.K2l)
        U0r = target.K1r.dot(target.K2r)
        U0l.real[abs(U0l.real) < eps] = 0.0
        U0l.imag[abs(U0l.imag) < eps] = 0.0
        U0r.real[abs(U0r.real) < eps] = 0.0
        U0r.imag[abs(U0r.imag) < eps] = 0.0
        return U0r, U0l