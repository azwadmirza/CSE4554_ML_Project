    def as_method(self):
        """
        Convert this signature to a bound method signature.
        """
        if self.recvr is not None:
            return self
        sig = signature(self.return_type, *self.args[1:],
                        recvr=self.args[0])
        return sig