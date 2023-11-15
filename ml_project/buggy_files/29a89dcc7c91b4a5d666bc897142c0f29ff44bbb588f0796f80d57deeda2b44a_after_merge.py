    def init_magics(self):
        super(ZMQInteractiveShell, self).init_magics()
        self.register_magics(KernelMagics)
        self.run_line_magic('alias_magic', 'ed edit')