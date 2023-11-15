    def experiment(self) -> Experiment:
        r"""
        Actual Neptune object. To use neptune features in your
        :class:`~pytorch_lightning.core.lightning.LightningModule` do the following.

        Example::

            self.logger.experiment.some_neptune_function()

        """

        if self._experiment is None:
            self._experiment = neptune.create_experiment(
                name=self.experiment_name,
                params=self.params,
                properties=self.properties,
                tags=self.tags,
                upload_source_files=self.upload_source_files,
                **self._kwargs)
        return self._experiment