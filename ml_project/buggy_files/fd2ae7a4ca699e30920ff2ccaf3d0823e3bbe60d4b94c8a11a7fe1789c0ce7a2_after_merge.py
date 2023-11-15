    def fail(self, msg: str, ctx: Context, *, blocker: bool = False) -> None:
        self.errors.report(ctx.get_line(), msg)