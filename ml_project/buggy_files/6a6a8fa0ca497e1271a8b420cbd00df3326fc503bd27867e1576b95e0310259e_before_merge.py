    def bridge(self):
        import leo.core.leoBridge as leoBridge
        return leoBridge.controller(gui='nullGui',
            loadPlugins=False,
            readSettings=False,
            silent=False,
            verbose=False)