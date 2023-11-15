    def indicatorInit(self):
        """
        Try init the distro specific appindicator,
        for example the Ubuntu MessagingMenu
        """
        def _noop_update(*args, **kwargs):
            pass

        try:
            self.indicatorUpdate = get_plugin('indicator')(self)
        except (NameError, TypeError):
            logger.warning("No indicator plugin found")
            self.indicatorUpdate = _noop_update