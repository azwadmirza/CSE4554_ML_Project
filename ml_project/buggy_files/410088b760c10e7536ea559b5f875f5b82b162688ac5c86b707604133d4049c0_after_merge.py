    def report(self, msg: str, context: Context, severity: str, file: str = None) -> None:
        """Report an error or note (unless disabled)."""
        if self.disable_count <= 0:
            self.errors.report(context.get_line() if context else -1,
                               msg.strip(), severity=severity, file=file)