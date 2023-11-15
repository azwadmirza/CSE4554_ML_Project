    def filter(self, record):
        # type: (logging.LogRecord) -> bool
        if getattr(record, 'skip_warningsiserror', False):
            # disabled by DisableWarningIsErrorFilter
            return True
        elif self.app.warningiserror:
            location = getattr(record, 'location', '')
            if location:
                raise SphinxWarning(location + ":" + record.msg % record.args)
            else:
                raise SphinxWarning(record.msg % record.args)
        else:
            return True