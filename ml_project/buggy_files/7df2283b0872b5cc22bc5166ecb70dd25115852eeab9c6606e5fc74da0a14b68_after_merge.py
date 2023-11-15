    def simulate_values(cls, num_events, schedulers, **kwargs):
        """Method to simulate scheduled values during num_events events.

        Args:
            num_events (int): number of events during the simulation.
            lr_schedulers (subclass of `torch.optim.lr_scheduler._LRScheduler`): lr_scheduler object to wrap.

        Returns:
            list of pairs: [event_index, value]

        """

        # This scheduler uses `torch.optim.lr_scheduler._LRScheduler` which
        # should be replicated in order to simulate LR values and
        # not perturb original scheduler.
        with tempfile.TemporaryDirectory() as tmpdirname:
            cache_filepath = Path(tmpdirname) / "ignite_lr_scheduler_cache.pt"
            objs = {"lr_scheduler_{}".format(i): s.state_dict() for i, s in enumerate(schedulers)}
            # all schedulers should be related to the same optimizer
            objs["optimizer"] = schedulers[0].optimizer.state_dict()

            torch.save(objs, cache_filepath.as_posix())

            values = []
            scheduler = cls(schedulers=schedulers, **kwargs)
            for i in range(num_events):
                params = scheduler.get_param()
                values.append([i] + params)
                scheduler(engine=None)

            objs = torch.load(cache_filepath.as_posix())
            for i, s in enumerate(schedulers):
                s.load_state_dict(objs["lr_scheduler_{}".format(i)])
                s.optimizer.load_state_dict(objs["optimizer"])

            return values