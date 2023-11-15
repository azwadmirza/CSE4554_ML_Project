    def filter(self, record):
        # type: (logging.LogRecord) -> bool
        if getattr(record, 'skip_warningsiserror', False):
            # disabled by DisableWarningIsErrorFilter
            return True
        elif self.app.warningiserror:
            location = getattr(record, 'location', '')
            message = record.msg.replace('%', '%%')
            if location:
                raise SphinxWarning(location + ":" + message % record.args)
            else:
                raise SphinxWarning(message % record.args)
        else:
            return True