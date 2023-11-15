    def fail(self, msg: str, ctx: Context, serious: bool = False) -> None:
        if (not serious and
                not self.check_untyped_defs and
                self.function_stack and
                self.function_stack[-1].is_dynamic()):
            return
        self.errors.report(ctx.get_line(), msg)