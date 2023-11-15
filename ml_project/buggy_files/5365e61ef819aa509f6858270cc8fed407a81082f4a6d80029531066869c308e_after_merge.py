    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 3:
            raise ValueError("Expected 3 datasets, got %d" %
                             (len(projectables), ))

        # Collect information that is the same between the projectables
        info = combine_metadata(*projectables)
        # Update that information with configured information (including name)
        info.update(self.attrs)
        # Force certain pieces of metadata that we *know* to be true
        info["wavelength"] = None
        info["mode"] = self.attrs.get("mode", "RGB")
        return Dataset(data=np.rollaxis(
            np.ma.dstack([projectable for projectable in projectables]),
            axis=2),
            **info)