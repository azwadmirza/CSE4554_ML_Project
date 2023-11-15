    def log(
        self,
        name: str,
        value: Any,
        prog_bar: bool = False,
        logger: bool = True,
        on_step: Optional[bool] = None,
        on_epoch: Optional[bool] = None,
        reduce_fx: Callable = torch.mean,
        tbptt_reduce_fx: Callable = torch.mean,
        tbptt_pad_token: int = 0,
        enable_graph: bool = False,
        sync_dist: bool = False,
        sync_dist_op: Union[Any, str] = 'mean',
        sync_dist_group: Optional[Any] = None,
    ):
        """
        Log a key, value

        Example::

            self.log('train_loss', loss)

        The default behavior per hook is as follows

        .. csv-table:: ``*`` also applies to the test loop
           :header: "LightningMoule Hook", "on_step", "on_epoch", "prog_bar", "logger"
           :widths: 20, 10, 10, 10, 10

           "training_step", "T", "F", "F", "T"
           "training_step_end", "T", "F", "F", "T"
           "training_epoch_end", "F", "T", "F", "T"
           "validation_step*", "F", "T", "F", "T"
           "validation_step_end*", "F", "T", "F", "T"
           "validation_epoch_end*", "F", "T", "F", "T"

        Args:
            name: key name
            value: value name
            prog_bar: if True logs to the progress bar
            logger: if True logs to the logger
            on_step: if True logs at this step. None auto-logs at the training_step but not validation/test_step
            on_epoch: if True logs epoch accumulated metrics. None auto-logs at the val/test step but not training_step
            reduce_fx: reduction function over step values for end of epoch. Torch.mean by default
            tbptt_reduce_fx: function to reduce on truncated back prop
            tbptt_pad_token: token to use for padding
            enable_graph: if True, will not auto detach the graph
            sync_dist: if True, reduces the metric across GPUs/TPUs
            sync_dist_op: the op to sync across GPUs/TPUs
            sync_dist_group: the ddp group
        """
        if self._results is not None:
            # in any epoch end can't log step metrics (only epoch metric)
            if 'epoch_end' in self._current_fx_name and on_step:
                m = f'on_step=True cannot be used on {self._current_fx_name} method'
                raise MisconfigurationException(m)

            if 'epoch_end' in self._current_fx_name and on_epoch is False:
                m = f'on_epoch cannot be False when called from the {self._current_fx_name} method'
                raise MisconfigurationException(m)

            # add log_dict
            # TODO: if logged twice fail with crash

            # set the default depending on the fx_name
            on_step = self.__auto_choose_log_on_step(on_step)
            on_epoch = self.__auto_choose_log_on_epoch(on_epoch)

            if self._current_hook_fx_name is not None:
                self.trainer.logger_connector.check_logging_in_callbacks(
                    self._current_hook_fx_name,
                    on_step=on_step,
                    on_epoch=on_epoch
                )

            # make sure user doesn't introduce logic for multi-dataloaders
            if "/dataloader_idx_" in name:
                raise MisconfigurationException(
                    f"Logged key: {name} should not contain information about dataloader_idx.")

            accelerator = self.trainer.accelerator_backend

            self._results.log(
                name,
                value,
                prog_bar,
                logger,
                on_step,
                on_epoch,
                reduce_fx,
                tbptt_reduce_fx,
                tbptt_pad_token,
                enable_graph,
                sync_dist,
                sync_dist_op,
                sync_dist_group,
                accelerator.sync_tensor,
                self._current_dataloader_idx,
            )