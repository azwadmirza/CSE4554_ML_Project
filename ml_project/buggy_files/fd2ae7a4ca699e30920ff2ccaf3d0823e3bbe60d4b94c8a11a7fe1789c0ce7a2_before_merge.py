    def fail(self, msg: str, ctx: Context) -> None:
        self.errors.report(ctx.get_line(), msg)