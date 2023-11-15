                def cjac(x, *args):
                    return approx_jacobian(x, fun, epsilon, *args)