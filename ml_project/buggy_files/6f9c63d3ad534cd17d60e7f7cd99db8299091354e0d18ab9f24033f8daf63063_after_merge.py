    def _track_callback_metrics(self, eval_results, using_eval_result):
        if len(eval_results) > 0 and (eval_results[0] is None or not isinstance(eval_results[0], Result)):
            return

        if using_eval_result:
            if isinstance(eval_results, list):
                for eval_result in eval_results:
                    self.trainer.logger_connector.callback_metrics.update(eval_result.callback_metrics)
                    self.trainer.logger_connector.evaluation_callback_metrics.update(eval_result.callback_metrics)
            else:
                self.trainer.logger_connector.callback_metrics.update(eval_results.callback_metrics)
                self.trainer.logger_connector.evaluation_callback_metrics.update(eval_results.callback_metrics)
        else:
            flat = {}
            if isinstance(eval_results, list):
                for eval_result in eval_results:
                    # with a scalar return, auto set it to "val_loss" for callbacks
                    if isinstance(eval_result, torch.Tensor):
                        flat = {'val_loss': eval_result}
                    elif isinstance(eval_result, dict):
                        flat = flatten_dict(eval_result)

                    # removing val_loss magic word to map to checkpoint + ES callback
                    if 'val_loss' in flat:
                        flat['checkpoint_on'] = flat['val_loss']
                        flat['early_stop_on'] = flat['val_loss']
                    self.trainer.logger_connector.callback_metrics.update(flat)
                    self.trainer.logger_connector.evaluation_callback_metrics.update(flat)
            else:
                # with a scalar return, auto set it to "val_loss" for callbacks
                if isinstance(eval_results, torch.Tensor):
                    flat = {'val_loss': eval_results}
                else:
                    flat = flatten_dict(eval_results)

                # removing val_loss magic word to map to checkpoint + ES callback
                if 'val_loss' in flat:
                    flat['checkpoint_on'] = flat['val_loss']
                    flat['early_stop_on'] = flat['val_loss']
                self.trainer.logger_connector.callback_metrics.update(flat)
                self.trainer.logger_connector.evaluation_callback_metrics.update(flat)