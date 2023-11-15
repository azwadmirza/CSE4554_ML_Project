    def link_error(self, sig):
        sig = sig.clone().set(immutable=True)
        return self.tasks[0].link_error(sig)