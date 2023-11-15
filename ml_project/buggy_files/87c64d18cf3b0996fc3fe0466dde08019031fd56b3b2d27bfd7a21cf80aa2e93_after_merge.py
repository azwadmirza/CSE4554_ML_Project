    def name(self) -> str:
        # don't create an experiment if we don't have one
        name = self._experiment.project_name() if self._experiment else None
        return name