    def as_method(self):
        """
        Convert this signature to a bound method signature.
        """
        if self.recvr is not None:
            return self
        sig = signature(self.return_type, *self.args[1:],
                        recvr=self.args[0])

        # Adjust the python signature
        params = list(self.pysig.parameters.values())[1:]
        sig.pysig = utils.pySignature(
            parameters=params,
            return_annotation=self.pysig.return_annotation,
        )
        return sig