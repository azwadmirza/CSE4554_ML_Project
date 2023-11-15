    def simulate_values(cls, num_events, lr_scheduler, **kwargs):
        """Method to simulate scheduled values during num_events events.

        Args:
            num_events (int): number of events during the simulation.
            lr_scheduler (subclass of `torch.optim.lr_scheduler._LRScheduler`): lr_scheduler object to wrap.

        Returns:
            list of pairs: [event_index, value]

        """

        if not isinstance(lr_scheduler, _LRScheduler):
            raise TypeError(
                "Argument lr_scheduler should be a subclass of torch.optim.lr_scheduler._LRScheduler, "
                "but given {}".format(type(lr_scheduler))
            )

        # This scheduler uses `torch.optim.lr_scheduler._LRScheduler` which
        # should be replicated in order to simulate LR values and
        # not perturb original scheduler.
        with tempfile.TemporaryDirectory() as tmpdirname:
            cache_filepath = Path(tmpdirname) / "ignite_lr_scheduler_cache.pt"
            obj = {
                "lr_scheduler": lr_scheduler.state_dict(),
                "optimizer": lr_scheduler.optimizer.state_dict(),
            }
            torch.save(obj, cache_filepath.as_posix())

            values = []
            scheduler = cls(save_history=False, lr_scheduler=lr_scheduler, **kwargs)
            for i in range(num_events):
                params = [p[scheduler.param_name] for p in scheduler.optimizer_param_groups]
                values.append([i] + params)
                scheduler(engine=None)

            obj = torch.load(cache_filepath.as_posix())
            lr_scheduler.load_state_dict(obj["lr_scheduler"])
            lr_scheduler.optimizer.load_state_dict(obj["optimizer"])

            return values