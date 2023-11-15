def generic_expand(self, args, kws):
    assert not args
    assert not kws
    return signature(_expand_integer(self.this.dtype), recvr=self.this)