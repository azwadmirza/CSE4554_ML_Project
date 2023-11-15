def generic_expand(self, args, kws):
    return signature(_expand_integer(self.this.dtype), recvr=self.this)