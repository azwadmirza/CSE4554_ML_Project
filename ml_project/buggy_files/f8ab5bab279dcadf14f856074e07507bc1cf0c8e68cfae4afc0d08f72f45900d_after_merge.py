    def version(self) -> str:
        # don't create an experiment if we don't have one
        return self._experiment.id if self._experiment else None