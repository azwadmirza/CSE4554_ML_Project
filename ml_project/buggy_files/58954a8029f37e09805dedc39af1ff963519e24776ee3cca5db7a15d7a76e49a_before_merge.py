    def __init__(self, schedulers, durations, save_history=False):

        if not isinstance(schedulers, Sequence) or len(schedulers) < 2:
            raise ValueError(
                "Argument schedulers should be a sequence of more than one parameter schedulers, "
                "but given {}".format(schedulers)
            )

        if not isinstance(durations, Sequence) or not all([isinstance(t, numbers.Integral) for t in durations]):
            raise ValueError("Argument durations should be list/tuple of integers, " "but given {}".format(durations))

        if len(schedulers) != len(durations) + 1:
            raise ValueError(
                "Incorrect number schedulers or duration values, "
                "given {} and {}".format(len(schedulers), len(durations))
            )

        for i, scheduler in enumerate(schedulers):
            if not isinstance(scheduler, ParamScheduler):
                raise TypeError(
                    "Value at index {} of schedulers should be a parameter scheduler, "
                    "but given {}".format(i, type(scheduler))
                )

        self.schedulers = schedulers
        self.durations = durations
        super(ConcatScheduler, self).__init__(optimizer=_get_fake_optimizer(), param_name="", save_history=save_history)

        self._scheduler_index = 0
        self._current_scheduler = None
        self._current_duration = None
        self._setup_scheduler()
        self._state_attrs += ["_current_duration", "durations", "_scheduler_index"]