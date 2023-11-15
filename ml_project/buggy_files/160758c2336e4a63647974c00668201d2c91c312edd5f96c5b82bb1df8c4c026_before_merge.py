    def verbatim_error_ctx(self, msg, *args, **kwargs):
        """Context manager for printing multi-line error messages.

        Displays a start sequence "!!! {optional message}"
        and a matching end sequence "!!!".

        The string "!!!" can be used as a "tombstone" for searching.

        For arguments, see `_format_msg`.
        """
        cli_logger = self

        class VerbatimErorContextManager():
            def __enter__(self):
                cli_logger.error(cf.bold("!!! ") + msg, *args, **kwargs)

            def __exit__(self, type, value, tb):
                cli_logger.error(cf.bold("!!!"))

        return VerbatimErorContextManager()