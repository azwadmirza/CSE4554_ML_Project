    def _process_Stmt(self, whitelist=None):

        if whitelist is not None:
            # optimize whitelist lookups
            whitelist = set(whitelist)

        for stmt_idx, stmt in enumerate(self.block.vex.statements):
            if whitelist is not None and stmt_idx not in whitelist:
                continue
            self.stmt_idx = stmt_idx

            if type(stmt) is pyvex.IRStmt.IMark:
                # Note that we cannot skip IMarks as they are used later to trigger observation events
                # The bug caused by skipping IMarks is reported at https://github.com/angr/angr/pull/1150
                self.ins_addr = stmt.addr + stmt.delta

            self._handle_Stmt(stmt)

        if self.block.vex.jumpkind == 'Ijk_Call':
            handler = '_handle_function'
            if hasattr(self, handler):
                getattr(self, handler)(self._expr(self.block.vex.next))
            else:
                self.l.warning('Function handler not implemented.')