    def __init__(self, schedulers: List[ParamScheduler], names: Optional[List[str]] = None, save_history=False):
        if not (
            isinstance(schedulers, Sequence) and all(isinstance(scheduler, ParamScheduler) for scheduler in schedulers)
        ):
            raise ValueError("Argument schedulers should be a list/tuple of parameter schedulers")

        if names is None:
            names = [s.param_name for s in schedulers]

        if not (isinstance(names, (list, tuple)) and all(isinstance(n, str) for n in names)):
            raise ValueError("Argument names should be a list/tuple of parameter scheduler's names")

        if len(names) != len(schedulers):
            raise ValueError("{} should be equal {}".format(len(schedulers), len(names)))

        self.schedulers = schedulers
        self.names = names

        optimizer = self.schedulers[0].optimizer
        if not (all(id(s.optimizer) == id(optimizer) for s in schedulers)):
            raise ValueError("schedulers should be related to same optimizer")

        super(ParamGroupScheduler, self).__init__(optimizer=optimizer, param_name="lr", save_history=save_history)