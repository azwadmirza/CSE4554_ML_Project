    def transfer_distrib_spawn_state_on_fit_end(self, results):
        # TODO: is there a better way than accessing callback through model -> trainer -> callback?
        best_model_path = self.lightning_module.trainer.checkpoint_callback.best_model_path

        if self.mp_queue is not None:
            rank_zero_warn("cleaning up ddp environment...")

            # save the last weights
            last_path = None
            # TODO: is there a better way than accessing trainer through model -> trainer?
            if not self.lightning_module.trainer.testing and best_model_path is not None and len(best_model_path) > 0:
                last_path = re.sub(".ckpt", ".tmp_end.ckpt", best_model_path)
                self.save(self.lightning_module.state_dict(), last_path)

            if self.global_rank == 0:
                # todo, pass complete checkpoint as state dictionary
                self.mp_queue.put(best_model_path)
                self.mp_queue.put(last_path)
                self.mp_queue.put(results)