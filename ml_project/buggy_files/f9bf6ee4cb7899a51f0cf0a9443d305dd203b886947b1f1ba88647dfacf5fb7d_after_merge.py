    def _stats(self, c):
        return (c+1.0)/3.0, (1.0-c+c*c)/18, sqrt(2)*(2*c-1)*(c+1)*(c-2) / \
               (5 * np.power((1.0-c+c*c), 1.5)), -3.0/5.0