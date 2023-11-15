    def init_magics(self):
        super(ZMQInteractiveShell, self).init_magics()
        self.register_magics(KernelMagics)