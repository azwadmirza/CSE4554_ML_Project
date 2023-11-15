    def _get_support_mask(self):
        check_is_fitted(self, 'scores_')

        alpha = self.alpha
        sv = np.sort(self.pvalues_)
        selected = sv[sv < alpha * np.arange(len(self.pvalues_))]
        if selected.size == 0:
            return np.zeros_like(self.pvalues_, dtype=bool)
        return self.pvalues_ <= selected.max()