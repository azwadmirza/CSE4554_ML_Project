def create_lr_scheduler_with_warmup(
    lr_scheduler,
    warmup_start_value,
    warmup_duration,
    warmup_end_value=None,
    save_history=False,
    output_simulated_values=None,
):
    """
    Helper method to create a learning rate scheduler with a linear warm-up.

    Args:
        lr_scheduler (ParamScheduler or subclass of `torch.optim.lr_scheduler._LRScheduler`): learning rate scheduler
            after the warm-up.
        warmup_start_value (float): learning rate start value of the warm-up phase.
        warmup_duration (int): warm-up phase duration, number of events.
        warmup_end_value (float): learning rate end value of the warm-up phase, (default=None). If None,
             warmup_end_value is set to optimizer initial lr.
        save_history (bool, optional): whether to log the parameter values to
            `engine.state.param_history`, (default=False).
        output_simulated_values (list, optional): optional output of simulated learning rate values.
            If output_simulated_values is a list of None, e.g. `[None] * 100`, after the execution it will be filled
            by 100 simulated learning rate values.

    Returns:
        ConcatScheduler: learning rate scheduler with linear warm-up.

    Note:
        If the first learning rate value provided by `lr_scheduler` is different from `warmup_end_value`, an additional
        event is added after the warm-up phase such that the warm-up ends with `warmup_end_value` value and then
        `lr_scheduler` provides its learning rate values as normally.

    Examples:

        .. code-block:: python

            torch_lr_scheduler = ExponentialLR(optimizer=optimizer, gamma=0.98)
            lr_values = [None] * 100
            scheduler = create_lr_scheduler_with_warmup(torch_lr_scheduler,
                                                        warmup_start_value=0.0,
                                                        warmup_end_value=0.1,
                                                        warmup_duration=10,
                                                        output_simulated_values=lr_values)
            lr_values = np.array(lr_values)
            # Plot simulated values
            plt.plot(lr_values[:, 0], lr_values[:, 1], label="learning rate")

            # Attach to the trainer
            trainer.add_event_handler(Events.ITERATION_STARTED, scheduler)

    """
    if not isinstance(lr_scheduler, (ParamScheduler, _LRScheduler)):
        raise TypeError(
            "Argument lr_scheduler should be a subclass of torch.optim.lr_scheduler._LRScheduler or "
            "ParamScheduler, but given {}".format(type(lr_scheduler))
        )

    if not (isinstance(warmup_duration, numbers.Integral) and warmup_duration > 1):
        raise ValueError("Argument warmup_duration should be at least 2 events, but given {}".format(warmup_duration))

    warmup_schedulers = []

    for param_group_index, param_group in enumerate(lr_scheduler.optimizer.param_groups):

        if warmup_end_value is None:
            param_group_warmup_end_value = param_group["lr"]
        else:
            param_group_warmup_end_value = warmup_end_value

        milestones_values = [(0, warmup_start_value), (warmup_duration - 1, param_group_warmup_end_value)]

        if isinstance(lr_scheduler, _LRScheduler):
            init_lr = param_group["lr"]

            if init_lr != param_group_warmup_end_value:
                milestones_values.append((warmup_duration, init_lr))

            lr_scheduler = LRScheduler(lr_scheduler)
        else:
            init_lr = lr_scheduler.get_param()
            if init_lr == param_group_warmup_end_value:
                if warmup_duration > 2:
                    d = (param_group_warmup_end_value - warmup_start_value) / (warmup_duration - 1)
                    milestones_values[-1] = (warmup_duration - 2, param_group_warmup_end_value - d)
                else:
                    milestones_values.pop(-1)

        warmup_scheduler = PiecewiseLinear(
            lr_scheduler.optimizer,
            param_name="lr",
            milestones_values=milestones_values,
            param_group_index=param_group_index,
            save_history=save_history,
        )

        warmup_schedulers.append(warmup_scheduler)

    warmup_scheduler = ParamGroupScheduler(warmup_schedulers, save_history=save_history)

    schedulers = [warmup_scheduler, lr_scheduler]
    durations = [
        milestones_values[-1][0] + 1,
    ]
    combined_scheduler = ConcatScheduler(schedulers, durations=durations, save_history=save_history)

    if output_simulated_values is not None:
        if not isinstance(output_simulated_values, list):
            raise TypeError(
                "Argument output_simulated_values should be a list of None, e.g. `[None] * 100`, "
                "but given {}.".format(type(output_simulated_values))
            )
        num_events = len(output_simulated_values)
        result = ConcatScheduler.simulate_values(num_events=num_events, schedulers=schedulers, durations=durations)
        for i in range(num_events):
            output_simulated_values[i] = result[i]
    return combined_scheduler