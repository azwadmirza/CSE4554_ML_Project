    def finders(self):
        from .vendor.pythonfinder import Finder
        finders = [
            Finder(path=self.env_paths["scripts"], global_search=gs, system=False)
            for gs in (False, True)
        ]
        return finders