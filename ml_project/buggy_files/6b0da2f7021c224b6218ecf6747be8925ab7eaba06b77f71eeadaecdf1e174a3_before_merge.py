    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 5:
            raise ValueError("Expected 5 datasets, got %d" %
                             (len(projectables), ))

        # Collect information that is the same between the projectables
        info = combine_info(*projectables)
        # Update that information with configured information (including name)
        info.update(self.info)
        # Force certain pieces of metadata that we *know* to be true
        info["wavelength"] = None
        info["mode"] = self.info.get("mode", "RGB")

        m07 = projectables[0]*255./160.
        m08 = projectables[1]*255./160.
        m09 = projectables[2]*255./160.
        m10 = projectables[3]*255./160.
        m11 = projectables[4]*255./160.
        refcu = m11 - m10
        refcu[refcu < 0] = 0

        ch1 = m07 - refcu / 2. - m09 / 4.
        ch2 = m08 + refcu / 4. + m09 / 4.
        ch3 = m11 + m09

        return Dataset(data=[ch1, ch2, ch3], **info)