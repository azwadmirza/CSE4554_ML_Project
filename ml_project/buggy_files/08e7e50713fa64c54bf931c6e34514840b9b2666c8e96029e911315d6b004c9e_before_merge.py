        def make_frame(t):

            played_parts = [clip.is_playing(t) for clip in self.clips]

            sounds = [
                clip.get_frame(t - clip.start) * np.array([part]).T
                for clip, part in zip(self.clips, played_parts)
                if (part is not False)
            ]

            if isinstance(t, np.ndarray):
                zero = np.zeros((len(t), self.nchannels))

            else:
                zero = np.zeros(self.nchannels)

            return zero + sum(sounds)