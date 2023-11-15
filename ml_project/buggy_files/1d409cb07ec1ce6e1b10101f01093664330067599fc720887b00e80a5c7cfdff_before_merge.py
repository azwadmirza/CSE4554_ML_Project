    def simulate_values(cls, num_events, schedulers, durations, param_names=None, **kwargs):
        """Method to simulate scheduled values during num_events events.

        Args:
            num_events (int): number of events during the simulation.
            schedulers (list of ParamScheduler): list of parameter schedulers.
            durations (list of int): list of number of events that lasts a parameter scheduler from schedulers.
            param_names (list or tuple of str, optional): parameter name or list of parameter names to simulate values.
                By default, the first scheduler's parameter name is taken.

        Returns:
            list of [event_index, value_0, value_1, ...], where values correspond to `param_names`.

        """
        if param_names is not None and not isinstance(param_names, (list, tuple)):
            raise ValueError("Argument param_names should be list or tuple of strings")
        output = []

        # Need to copy all schedulers otherwise unsafe
        copy_schedulers = [_replicate_scheduler(s) for s in schedulers]

        scheduler = cls(copy_schedulers, durations, save_history=False)
        if param_names is None:
            param_names = [scheduler.param_name]
        for i in range(num_events):
            scheduler(engine=None)
            values = [i]
            for param_name in param_names:
                params = [p[param_name] for p in scheduler.optimizer_param_groups]
                values = values + params
            output.append(values)
        return output