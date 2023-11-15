    def f(n):
        poly = np.array([1, np.log(n), np.log(n) ** 2])
        return np.exp(poly.dot(params.T))