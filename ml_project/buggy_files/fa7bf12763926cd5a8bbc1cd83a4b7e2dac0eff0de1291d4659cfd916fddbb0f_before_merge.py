    def __repr__(self):
        return "<XRef %s: %s->%s>" % (
                XRefType.to_string(self.type),
                "%#x" % self.ins_addr if self.ins_addr is not None else "%#x[%d]" % (self.block_addr, self.stmt_idx),
                "%#x" % (self.dst if self.dst is not None else self.memory_data.addr)
        )