    def __init__(
        self, cfg: DictConfig, fairseq_optimizer
    ):
        super().__init__(cfg, fairseq_optimizer)
        if isinstance(cfg.lr, Collection) and len(cfg.lr) > 1:
            raise ValueError(
                "Cannot use a fixed learning rate schedule with cosine."
                " Consider --lr-scheduler=fixed instead."
            )

        warmup_end_lr = cfg.max_lr
        lr = (
            cfg.lr[0]
            if isinstance(cfg.lr, Collection)
            else cfg.lr
        )
        if cfg.warmup_init_lr < 0:
            cfg.warmup_init_lr = lr

        self.min_lr = lr
        self.max_lr = cfg.max_lr
        assert self.max_lr > self.min_lr, "max_lr must be more than lr"

        self.t_mult = cfg.t_mult
        self.period = cfg.lr_period_updates

        if self.period <= 0:
            assert (
                cfg.max_update >= 0
            ), "Either --max_update or --lr-period-updates must be set"
            self.period = cfg.max_update - cfg.warmup_updates

        if cfg.warmup_updates > 0:
            # linearly warmup for the first args.warmup_updates
            self.lr_step = (
                warmup_end_lr - cfg.warmup_init_lr
            ) / cfg.warmup_updates
        else:
            self.lr_step = 1

        self.warmup_updates = cfg.warmup_updates
        self.lr_shrink = cfg.lr_shrink

        # initial learning rate
        self.lr = cfg.warmup_init_lr
        self.optimizer.set_lr(self.lr)