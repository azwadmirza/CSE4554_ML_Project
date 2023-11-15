    def __init__(self, mu=0.0, sd=None, tau=None, alpha=1,  *args, **kwargs):
        super(SkewNormal, self).__init__(*args, **kwargs)
        self.mu = mu
        self.tau, self.sd = get_tau_sd(tau=tau, sd=sd)
        self.alpha = alpha
        self.mean = mu + self.sd * (2 / np.pi)**0.5 * alpha / (1 + alpha**2)**0.5
        self.variance = self.sd**2 * (1 - (2 * alpha**2) / ((1 + alpha**2) * np.pi))

        assert_negative_support(tau, 'tau', 'SkewNormal')
        assert_negative_support(sd, 'sd', 'SkewNormal')