    def simulate_values(cls, num_events, schedulers, **kwargs):
        """Method to simulate scheduled values during num_events events.

        Args:
            num_events (int): number of events during the simulation.
            lr_schedulers (subclass of `torch.optim.lr_scheduler._LRScheduler`): lr_scheduler object to wrap.

        Returns:
            list of pairs: [event_index, value]

        """
        copy_lr_schedulers = [_replicate_scheduler(s) for s in schedulers]
        values = []
        scheduler = cls(schedulers=copy_lr_schedulers)
        for i in range(num_events):
            scheduler(engine=None)
            params = scheduler.get_param()
            values.append([i] + params)
        return values