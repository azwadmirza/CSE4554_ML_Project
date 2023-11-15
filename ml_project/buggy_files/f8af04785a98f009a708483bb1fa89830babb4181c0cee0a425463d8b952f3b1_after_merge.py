    def link_error(self, sig):
        try:
            sig = sig.clone().set(immutable=True)
        except AttributeError:
            # See issue #5265.  I don't use isinstance because current tests
            # pass a Mock object as argument.
            sig['immutable'] = True
            sig = Signature.from_dict(sig)
        return self.tasks[0].link_error(sig)