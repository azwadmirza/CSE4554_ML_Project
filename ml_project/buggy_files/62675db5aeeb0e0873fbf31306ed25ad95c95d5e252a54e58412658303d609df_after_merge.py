    def _print(self,
               msg: str,
               _level_str: str = "INFO",
               _linefeed: bool = True):
        """Proxy for printing messages.

        Args:
            msg (str): Message to print.
            linefeed (bool):
                If `linefeed` is `False` no linefeed is printed at the
                end of the message.
        """
        if self.pretty:
            rendered_message = "  " * self.indent_level + msg
        else:
            if msg.strip() == "":
                return
            caller_info = _external_caller_info()
            record = logging.LogRecord(
                name="cli",
                # We override the level name later
                # TODO(maximsmol): give approximate level #s to our log levels
                level=0,
                # The user-facing logs do not need this information anyway
                # and it would be very tedious to extract since _print
                # can be at varying depths in the call stack
                # TODO(maximsmol): do it anyway to be extra
                pathname=caller_info["filename"],
                lineno=caller_info["lineno"],
                msg=msg,
                args={},
                # No exception
                exc_info=None)
            record.levelname = _level_str
            rendered_message = self._formatter.format(record)

        # We aren't using standard python logging convention, so we hardcode
        # the log levels for now.
        if _level_str in ["WARNING", "ERROR", "PANIC"]:
            stream = sys.stderr
        else:
            stream = sys.stdout

        if not _linefeed:
            stream.write(rendered_message)
            stream.flush()
            return

        print(rendered_message, file=stream)