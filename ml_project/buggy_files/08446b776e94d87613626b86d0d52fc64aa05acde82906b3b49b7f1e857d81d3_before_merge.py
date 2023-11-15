    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 2:
            raise ValueError("Expected 2 datasets, got %d" %
                             (len(projectables), ))

        p1, p2 = projectables
        fog = p1 - p2
        fog.info.update(self.info)
        fog.info["area"] = p1.info["area"]
        fog.info["start_time"] = p1.info["start_time"]
        fog.info["end_time"] = p1.info["end_time"]
        fog.info["name"] = self.info["name"]
        fog.info["wavelength"] = None
        fog.info.setdefault("mode", "L")
        return fog