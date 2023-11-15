    def index(self, level=logger.ERROR, **kwargs):
        """Default index page."""
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = logger.ERROR

        t = PageTemplate(rh=self, filename='errorlogs.mako')
        return t.render(header='Logs &amp; Errors', title='Logs &amp; Errors', topmenu='system',
                        submenu=self._create_menu(level), logLevel=level, controller='errorlogs', action='index')