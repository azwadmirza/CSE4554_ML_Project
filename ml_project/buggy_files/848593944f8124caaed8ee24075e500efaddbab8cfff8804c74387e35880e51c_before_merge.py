    def __init__(self, dist, group_val=None):
        self.dist = dist
        self.n = n = np.sum(dist[1])
        if n == 0:
            return
        self.a_min = float(dist[0, 0])
        self.a_max = float(dist[0, -1])
        self.mean = float(np.sum(dist[0] * dist[1]) / n)
        self.var = float(np.sum(dist[1] * (dist[0] - self.mean) ** 2) / n)
        self.dev = math.sqrt(self.var)
        a, freq = np.asarray(dist)
        q25, median, q75 = _quantiles(a, freq, [0.25, 0.5, 0.75])
        self.median = median
        # The code below omits the q25 or q75 in the plot when they are None
        self.q25 = None if q25 == median else q25
        self.q75 = None if q75 == median else q75
        self.data_range = ContDataRange(self.q25, self.q75, group_val)