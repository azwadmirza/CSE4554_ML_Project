def get_corr_func(method):
    if method in ['kendall', 'spearman']:
        from scipy.stats import kendalltau, spearmanr

    def _pearson(a, b):
        return np.corrcoef(a, b)[0, 1]
    def _kendall(a, b):
        return kendalltau(a, b)[0]
    def _spearman(a, b):
        return spearmanr(a, b)[0]

    _cor_methods = {
        'pearson' : _pearson,
        'kendall' : _kendall,
        'spearman' : _spearman
    }
    return _cor_methods[method]