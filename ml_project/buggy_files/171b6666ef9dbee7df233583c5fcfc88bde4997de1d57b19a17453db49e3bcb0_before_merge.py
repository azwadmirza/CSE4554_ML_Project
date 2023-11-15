    def stats(self):
        if not self.count:
            quantiles = []
        else:
            quantiles = np.percentile(self.items[:self.count],
                                      [0, 10, 50, 90, 100]).tolist()
        return {
            self.name + "_count": int(self.count),
            self.name + "_mean": float(np.mean(self.items[:self.count])),
            self.name + "_std": float(np.std(self.items[:self.count])),
            self.name + "_quantiles": quantiles,
        }