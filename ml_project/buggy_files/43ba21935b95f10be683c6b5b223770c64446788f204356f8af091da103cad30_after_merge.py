    def run(self):
        clean_tables()
        build_tables()
        # install Jupyter hook
        root = self.root if self.root else None
        prefix = self.prefix if self.prefix else None
        try:
            install_jupyter_hook(prefix=prefix, root=root)
        except Exception:
            import traceback
            traceback.print_exc()
            print('Installing Jupyter hook failed.')
        install.run(self)