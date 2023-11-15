    def __run_ddp_spawn(self, model, nprocs):
        self.set_random_port()

        # pass in a state q
        smp = mp.get_context('spawn')
        q = smp.SimpleQueue()

        mp.spawn(self.ddp_train, nprocs=nprocs, args=(q, model,))

        # restore main state with best weights
        best_path = q.get()
        results = q.get()
        last_path = q.get()

        # transfer back the best path to the trainer
        self.checkpoint_callback.best_model_path = best_path

        # load last weights
        if last_path is not None and not self.testing:
            torch.load(last_path, map_location=lambda storage, loc: storage)

        self.model = model
        return results