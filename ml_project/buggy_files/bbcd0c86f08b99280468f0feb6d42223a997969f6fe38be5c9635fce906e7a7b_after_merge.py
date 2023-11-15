    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, 'skip_warningsiserror', False):
            # disabled by DisableWarningIsErrorFilter
            return True
        elif self.app.warningiserror:
            location = getattr(record, 'location', '')
            try:
                message = record.msg % record.args
            except (TypeError, ValueError):
                message = record.msg  # use record.msg itself

            if location:
                raise SphinxWarning(location + ":" + str(message))
            else:
                raise SphinxWarning(message)
        else:
            return True