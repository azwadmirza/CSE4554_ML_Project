    def get_gain(self, band: int):
        if band < 0 or band >= self.band_count:
            raise IndexError(f"Band {band} does not exist!")
        return self.bands[band]