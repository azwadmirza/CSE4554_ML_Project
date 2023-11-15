    def initialize_from_data_empspect(self, train_x, train_y):
        """
        Initialize mixture components based on the empirical spectrum of the data.

        This will often be better than the standard initialize_from_data method.
        """
        import numpy as np
        from scipy.fftpack import fft
        from scipy.integrate import cumtrapz

        if not torch.is_tensor(train_x) or not torch.is_tensor(train_y):
            raise RuntimeError("train_x and train_y should be tensors")
        if train_x.ndimension() == 1:
            train_x = train_x.unsqueeze(-1)

        N = train_x.size(-2)
        emp_spect = np.abs(fft(train_y.cpu().detach().numpy())) ** 2 / N
        M = math.floor(N / 2)

        freq1 = np.arange(M + 1)
        freq2 = np.arange(-M + 1, 0)
        freq = np.hstack((freq1, freq2)) / N
        freq = freq[: M + 1]
        emp_spect = emp_spect[: M + 1]

        total_area = np.trapz(emp_spect, freq)
        spec_cdf = np.hstack((np.zeros(1), cumtrapz(emp_spect, freq)))
        spec_cdf = spec_cdf / total_area

        a = np.random.rand(1000, self.ard_num_dims)
        p, q = np.histogram(a, spec_cdf)
        bins = np.digitize(a, q)
        slopes = (spec_cdf[bins] - spec_cdf[bins - 1]) / (freq[bins] - freq[bins - 1])
        intercepts = spec_cdf[bins - 1] - slopes * freq[bins - 1]
        inv_spec = (a - intercepts) / slopes

        from sklearn.mixture import GaussianMixture

        GMM = GaussianMixture(n_components=self.num_mixtures, covariance_type="diag").fit(inv_spec)
        means = GMM.means_
        varz = GMM.covariances_
        weights = GMM.weights_

        self.mixture_means = means
        self.mixture_scales = varz
        self.mixture_weights = weights