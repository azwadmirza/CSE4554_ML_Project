    def cache_result(self) -> None:
        """
        This function is called after every hook
        and store the result object
        """
        with self.trainer.profiler.profile("cache_result"):
            model_ref = self.trainer.get_model()

            # extract hook results
            hook_result = model_ref._results

            if len(hook_result) == 1:
                model_ref._current_hook_fx_name = None
                model_ref._current_fx_name = ''
                return

            # extract model information
            fx_name, dataloader_idx = self.current_model_info()

            # add only if anything as been logged
            # default len is 1 due to _internals

            if fx_name not in self._internals:
                self._internals[fx_name] = HookResultStore(fx_name)

            extra_info = {}
            if self.has_split_and_opt_idx:
                extra_info = self.extra_info

            # attach capture batch_size
            Result.attach_batch_size(self._batch_size, hook_result)

            hook_result.detach()
            if self.trainer.move_metrics_to_cpu:
                hook_result.cpu()
            elif self.trainer.use_dp:
                hook_result.to(torch.device("cuda", self.trainer.root_gpu))

            self._internals[fx_name].append(
                hook_result,
                dataloader_idx=dataloader_idx,
                extra_info=extra_info)

            # update logged_metrics, progress_bar_metrics, callback_metrics
            self.update_logger_connector(fx_name)

            self.reset_model()