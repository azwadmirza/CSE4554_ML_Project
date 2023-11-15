        def make_frame(t):
            """complicated, but must be able to handle the case where t
            is a list of the form sin(t)"""

            if isinstance(t, np.ndarray):
                array_inds = np.round(self.fps * t).astype(int)
                in_array = (array_inds >= 0) & (array_inds < len(self.array))
                result = np.zeros((len(t), 2))
                result[in_array] = self.array[array_inds[in_array]]
                return result
            else:
                i = int(self.fps * t)
                if i < 0 or i >= len(self.array):
                    return 0 * self.array[0]
                else:
                    return self.array[i]