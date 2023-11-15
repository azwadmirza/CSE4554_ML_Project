    def log_internal_error(self, exc: BaseException = None, message: str = None) -> None:
        if not message:
            # If exc exists, raise it so that sys.exc_info() is populated with its data.
            if exc:
                try:
                    raise exc
                except KeyboardInterrupt:
                    # Let KeyboardInterrupt bubble up.
                    raise
                except:  # noqa: E722, we want to catch everything
                    pass

            message = ''.join(traceback.format_exception(*sys.exc_info()))

        logger.error(message)

        try:
            # Strip ANSI from the message, since this might be a checker's CompileError ...we don't want to see the raw
            # ANSI codes from GCC/Clang on the site. We could use format_ansi and send HTML to the site, but the site
            # doesn't presently support HTML internal error formatting.
            self.packet_manager.internal_error_packet(strip_ansi(message))
        except Exception:  # noqa E722: don't want `log_internal_error` to trigger `log_internal_error`, ever
            logger.exception('Error encountered while reporting error to site!')