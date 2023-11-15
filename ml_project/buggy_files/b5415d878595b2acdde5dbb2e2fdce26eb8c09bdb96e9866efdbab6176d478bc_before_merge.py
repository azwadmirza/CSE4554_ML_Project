    def _stats(self, c):
        # See, for example, "A Statistical Study of Log-Gamma Distribution", by
        # Ping Shing Chan (thesis, McMaster University, 1993).
        mean = special.digamma(c)
        var = special.polygamma(1, c)
        skewness = special.polygamma(2, c) / var**1.5
        excess_kurtosis = special.polygamma(3, c) / (var*var)
        return mean, var, skewness, excess_kurtosis