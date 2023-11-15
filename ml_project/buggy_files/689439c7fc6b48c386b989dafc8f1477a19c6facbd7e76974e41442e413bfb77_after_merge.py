    def check_no_global(self, n: str, ctx: Context,
                        is_overloaded_func: bool = False) -> None:
        if n in self.globals:
            prev_is_overloaded = isinstance(self.globals[n], OverloadedFuncDef)
            if is_overloaded_func and prev_is_overloaded:
                self.fail("Nonconsecutive overload {} found".format(n), ctx)
            elif prev_is_overloaded:
                self.fail("Definition of '{}' missing 'overload'".format(n), ctx)
            else:
                self.name_already_defined(n, ctx)