    def __init__(self, lr_scheduler, save_history=False, **kwargs):

        if not isinstance(lr_scheduler, _LRScheduler):
            raise TypeError(
                "Argument lr_scheduler should be a subclass of torch.optim.lr_scheduler._LRScheduler, "
                "but given {}".format(type(lr_scheduler))
            )

        self.lr_scheduler = lr_scheduler
        super(LRScheduler, self).__init__(
            optimizer=self.lr_scheduler.optimizer, param_name="lr", save_history=save_history
        )
        self._state_attrs += [
            "lr_scheduler",
        ]