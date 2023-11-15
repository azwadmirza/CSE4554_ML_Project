    def experiment(self) -> Experiment:
        r"""
        Actual Neptune object. To use neptune features in your
        :class:`~pytorch_lightning.core.lightning.LightningModule` do the following.

        Example::

            self.logger.experiment.some_neptune_function()

        """

        # Note that even though we initialize self._experiment in __init__,
        # it may still end up being None after being pickled and un-pickled
        if self._experiment is None:
            self._experiment = self._create_or_get_experiment()

        return self._experiment