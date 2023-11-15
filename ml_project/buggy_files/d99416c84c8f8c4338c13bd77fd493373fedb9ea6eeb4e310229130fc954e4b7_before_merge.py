    def disable(self):
        # restore original meta_path to disable import hook
        sys.meta_path = self.orig_meta_path
        # remove mocked modules from sys.modules to avoid side effects after
        # running auto-documenter
        for m in self.mocked_modules:
            if m in sys.modules:
                del sys.modules[m]