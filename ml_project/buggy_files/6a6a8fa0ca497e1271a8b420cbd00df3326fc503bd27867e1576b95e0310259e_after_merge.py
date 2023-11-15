    def bridge(self):
        """Return an instance of Leo's bridge."""
        import leo.core.leoBridge as leoBridge
        return leoBridge.controller(gui='nullGui',
            loadPlugins=False,
            readSettings=False,
            silent=True,
            verbose=False,
        )