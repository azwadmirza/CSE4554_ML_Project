    def simulate_values(cls, num_events, lr_scheduler, **kwargs):
        """Method to simulate scheduled values during num_events events.

        Args:
            num_events (int): number of events during the simulation.
            lr_scheduler (subclass of `torch.optim.lr_scheduler._LRScheduler`): lr_scheduler object to wrap.

        Returns:
            list of pairs: [event_index, value]

        """
        # This scheduler uses `torch.optim.lr_scheduler._LRScheduler` which
        # should be replicated in order to simulate LR values and
        # not perturb original scheduler.
        copy_lr_scheduler = LRScheduler._replicate_lr_scheduler(lr_scheduler)
        values = []
        scheduler = cls(save_history=False, lr_scheduler=copy_lr_scheduler)
        for i in range(num_events):
            params = [p[scheduler.param_name] for p in scheduler.optimizer_param_groups]
            values.append([i] + params)
            scheduler(engine=None)

        return values