    def __sub__(self, other):
        import cftime
        if isinstance(other, (CFTimeIndex, cftime.datetime)):
            return pd.TimedeltaIndex(np.array(self) - np.array(other))
        elif isinstance(other, pd.TimedeltaIndex):
            return CFTimeIndex(np.array(self) - other.to_pytimedelta())
        else:
            return CFTimeIndex(np.array(self) - other)