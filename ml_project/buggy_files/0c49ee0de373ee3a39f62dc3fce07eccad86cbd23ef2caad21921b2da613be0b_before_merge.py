    def __run_ddp_spawn(self, model, nprocs):
        self.set_random_port()

        # pass in a state q
        smp = mp.get_context('spawn')
        q = smp.SimpleQueue()

        mp.spawn(self.ddp_train, nprocs=nprocs, args=(q, model,))

        # restore main state with best weights
        best_path = q.get()
        results = q.get()
        if best_path is not None and len(best_path) > 0:
            self.checkpoint_callback.best_model_path = best_path
            model.load_from_checkpoint(best_path)

        self.model = model
        return results