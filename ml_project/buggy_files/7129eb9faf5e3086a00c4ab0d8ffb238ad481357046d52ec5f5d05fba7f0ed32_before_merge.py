    def wrap(cls, ctx: DistributedContext, op):
        # import inside, or Ray backend may fail
        from .config import options

        if getattr(ctx, 'running_mode', RunningMode.local) == RunningMode.local or \
                options.custom_log_dir is None:
            # do nothing for local scheduler
            return func(cls, ctx, op)

        custom_log_meta = ctx.get_custom_log_meta_ref()
        log_path = gen_log_path(ctx.session_id, op.key)

        with _LogWrapper(ctx, op, log_path, custom_log_meta):
            return func(cls, ctx, op)