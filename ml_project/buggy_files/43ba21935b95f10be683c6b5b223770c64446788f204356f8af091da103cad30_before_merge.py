    def run(self):
        clean_tables()
        build_tables()
        install_jupyter_hook(self.root if self.root else None)
        install.run(self)