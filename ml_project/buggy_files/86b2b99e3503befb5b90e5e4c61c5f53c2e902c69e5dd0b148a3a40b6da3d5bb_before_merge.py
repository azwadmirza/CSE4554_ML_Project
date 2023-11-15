    def experiment(self) -> Run:
        r"""

          Actual wandb object. To use wandb features do the following.

          Example::

              self.logger.experiment.some_wandb_function()

          """
        if self._experiment is None:
            if self._offline:
                os.environ['WANDB_MODE'] = 'dryrun'
            self._experiment = wandb.init(
                name=self._name, dir=self._save_dir, project=self._project, anonymous=self._anonymous,
                id=self._id, resume='allow', tags=self._tags, entity=self._entity)
            # save checkpoints in wandb dir to upload on W&B servers
            if self._log_model:
                self.save_dir = self._experiment.dir
        return self._experiment