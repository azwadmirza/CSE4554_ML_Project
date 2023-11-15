    def write(self, logentry):
        if 'isError' not in logentry:
            logentry['isError'] = False

        if self.format == 'cef':
            self.syslog.emit({
                'message': cowrie.core.cef.formatCef(logentry),
                'isError': False,
                'system': 'cowrie'
            })
        else:
            # message appears with additional spaces if message key is defined
            logentry['message'] = [logentry['message']]
            self.syslog.emit(logentry)