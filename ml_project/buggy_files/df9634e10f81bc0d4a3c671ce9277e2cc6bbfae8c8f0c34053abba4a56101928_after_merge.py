    def set_gain(self, band: int, gain: float):
        if band < 0 or band >= self.band_count:
            raise IndexError(f"Band {band} does not exist!")

        gain = min(max(gain, -0.25), 1.0)

        self.bands[band] = gain