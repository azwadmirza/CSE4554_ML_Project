    def _save_last_checkpoint(self, trainer, pl_module, ckpt_name_metrics):
        should_save_last = self.monitor is None or self.save_last
        if not should_save_last:
            return

        # when user ALSO asked for the 'last.ckpt' change the name
        if self.save_last:
            last_filepath = self._format_checkpoint_name(
                self.CHECKPOINT_NAME_LAST,
                trainer.current_epoch,
                trainer.global_step,
                ckpt_name_metrics,
                prefix=self.prefix
            )
            last_filepath = os.path.join(self.dirpath, f"{last_filepath}{self.FILE_EXTENSION}")
        else:
            last_filepath = self._get_metric_interpolated_filepath_name(
                ckpt_name_metrics, trainer.current_epoch, trainer.global_step
            )

        accelerator_backend = trainer.accelerator_backend

        if accelerator_backend is not None and accelerator_backend.rpc_enabled:
            # RPCPlugin manages saving all model states
            accelerator_backend.ddp_plugin.rpc_save_model(self._save_model, last_filepath, trainer, pl_module)
        else:
            self._save_model(last_filepath, trainer, pl_module)
        if (
                self.last_model_path
                and self.last_model_path != last_filepath
                and (self.save_top_k != -1 or self.save_last)
                and trainer.is_global_zero
        ):
            self._del_model(self.last_model_path)
        self.last_model_path = last_filepath

        if self.monitor is None:
            self.best_model_path = self.last_model_path