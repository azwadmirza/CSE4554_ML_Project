    def index(self, level=logger.ERROR):
        try:
            level = int(level)
        except Exception:
            level = logger.ERROR

        t = PageTemplate(rh=self, filename='errorlogs.mako')
        return t.render(header='Logs &amp; Errors', title='Logs &amp; Errors',
                        topmenu='system', submenu=self.ErrorLogsMenu(level),
                        logLevel=level, controller='errorlogs', action='index')