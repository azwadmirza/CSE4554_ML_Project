    def __init__(self, x, kernel=None):
        x = np.asarray(x)
        if x.ndim == 1:
            x = x[:,None]

        nobs, n_series = x.shape

        if kernel is None:
            kernel = kernels.Gaussian()  # no meaningful bandwidth yet

        if n_series > 1:
            if isinstance( kernel, kernels.CustomKernel ):
                kernel = kernels.NdKernel(n_series, kernels = kernel)

        self.kernel = kernel
        self.n = n_series  #TODO change attribute
        self.x = x