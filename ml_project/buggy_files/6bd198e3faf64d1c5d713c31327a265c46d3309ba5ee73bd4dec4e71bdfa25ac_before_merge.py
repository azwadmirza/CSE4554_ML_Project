    def dispatch(self, state):
        inst = state.get_inst()
        _logger.debug("dispatch pc=%s, inst=%s", state._pc, inst)
        fn = getattr(self, "op_{}".format(inst.opname), None)
        if fn is not None:
            fn(state, inst)
        else:
            msg = "Use of unsupported opcode (%s) found" % inst.opname
            raise UnsupportedError(msg, loc=self.get_debug_loc(inst.lineno))