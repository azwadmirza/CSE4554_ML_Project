    def clip(self, fmt: str, f: flow.Flow) -> None:
        """
            Export a flow to the system clipboard.
        """
        if fmt not in formats:
            raise exceptions.CommandError("No such export format: %s" % fmt)
        func = formats[fmt]  # type: typing.Any
        v = strutils.always_str(func(f))
        try:
            pyperclip.copy(v)
        except pyperclip.PyperclipException as e:
            ctx.log.error(str(e))