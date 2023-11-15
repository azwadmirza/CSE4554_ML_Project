    def _from_numpy(self, data):
        buffer = BytesIO()
        wavfile.write(buffer, self.sample_rate, data)
        return buffer