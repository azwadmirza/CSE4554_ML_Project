    def _get_support_mask(self):
        check_is_fitted(self, 'scores_')

        alpha = self.alpha
        sv = np.sort(self.pvalues_)
        threshold = sv[sv < alpha * np.arange(len(self.pvalues_))].max()
        return self.pvalues_ <= threshold