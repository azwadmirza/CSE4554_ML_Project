    def __call__(self, direction, factor, values):
        angles_deg = values/factor
        damping_ratios = np.cos((180-angles_deg) * np.pi/180)
        ret = ["%.2f" % val for val in damping_ratios]
        return ret