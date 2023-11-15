    def __sub__(self, other):
        if isinstance(other, CFTimeIndex):
            return pd.TimedeltaIndex(np.array(self) - np.array(other))
        elif isinstance(other, pd.TimedeltaIndex):
            return CFTimeIndex(np.array(self) - other.to_pytimedelta())
        else:
            return CFTimeIndex(np.array(self) - other)