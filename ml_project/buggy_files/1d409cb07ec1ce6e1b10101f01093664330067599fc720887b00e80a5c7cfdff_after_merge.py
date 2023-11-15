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

        # This scheduler uses `ParamScheduler` which
        # should be replicated in order to simulate LR values and
        # not perturb original scheduler.
        with tempfile.TemporaryDirectory() as tmpdirname:
            cache_filepath = Path(tmpdirname) / "ignite_lr_scheduler_cache.pt"
            objs = {"lr_scheduler_{}".format(i): s.state_dict() for i, s in enumerate(schedulers)}
            # all schedulers should be related to the same optimizer
            objs["optimizer"] = schedulers[0].optimizer.state_dict()

            torch.save(objs, cache_filepath.as_posix())

            # do not save_history
            for s in schedulers:
                s.save_history = False

            output = []
            scheduler = cls(schedulers=schedulers, save_history=False, durations=durations, **kwargs)
            if param_names is None:
                param_names = [scheduler.param_name]
            for i in range(num_events):
                scheduler(engine=None)
                values = [i]
                for param_name in param_names:
                    params = [p[param_name] for p in scheduler.optimizer_param_groups]
                    values = values + params
                output.append(values)

            objs = torch.load(cache_filepath.as_posix())
            for i, s in enumerate(schedulers):
                s.load_state_dict(objs["lr_scheduler_{}".format(i)])
                s.optimizer.load_state_dict(objs["optimizer"])

            return output