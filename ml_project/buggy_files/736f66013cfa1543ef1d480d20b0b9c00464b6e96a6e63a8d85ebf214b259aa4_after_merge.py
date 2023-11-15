    def __init__(self, lam, *args, **kwargs):
        super(Exponential, self).__init__(*args, **kwargs)
        self.lam = lam = tt.as_tensor_variable(lam)
        self.mean = 1. / self.lam
        self.median = self.mean * tt.log(2)
        self.mode = tt.zeros_like(self.lam)

        self.variance = self.lam**-2

        assert_negative_support(lam, 'lam', 'Exponential')