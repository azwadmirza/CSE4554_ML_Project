    def __init__(self, mu=0, sigma=None, tau=None, lower=None, upper=None,
                 transform='auto', sd=None, *args, **kwargs):
        if sd is not None:
            sigma = sd
        tau, sigma = get_tau_sigma(tau=tau, sigma=sigma)
        self.sigma = self.sd = tt.as_tensor_variable(sigma)
        self.tau = tt.as_tensor_variable(tau)
        self.lower = tt.as_tensor_variable(floatX(lower)) if lower is not None else lower
        self.upper = tt.as_tensor_variable(floatX(upper)) if upper is not None else upper
        self.mu = tt.as_tensor_variable(floatX(mu))

        if self.lower is None and self.upper is None:
            self._defaultval = mu
        elif self.lower is None and self.upper is not None:
            self._defaultval = self.upper - 1.
        elif self.lower is not None and self.upper is None:
            self._defaultval = self.lower + 1.
        else:
            self._defaultval = (self.lower + self.upper) / 2

        assert_negative_support(sigma, 'sigma', 'TruncatedNormal')
        assert_negative_support(tau, 'tau', 'TruncatedNormal')

        super().__init__(defaults=('_defaultval',), transform=transform,
                         lower=lower, upper=upper, *args, **kwargs)