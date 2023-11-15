    def __repr__(self):
        return "<XRef %s: %s->%s>" % (
                self.type_string,
                "%#x" % self.ins_addr if self.ins_addr is not None else "%#x[%d]" % (self.block_addr, self.stmt_idx),
                "%s" % self.dst if self.dst is not None else "%#x" % (self.memory_data.addr)
        )