def approx_fhess_p(x0, p, fprime, epsilon, *args):
    f2 = fprime(*((x0 + epsilon*p,) + args))
    f1 = fprime(*((x0,) + args))
    return (f2 - f1) / epsilon