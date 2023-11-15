    def _make_returns(self, ail_graph: networkx.DiGraph) -> networkx.DiGraph:
        """
        Work on each return statement and fill in its return expressions.
        """

        if self.function.calling_convention is None:
            # unknown calling convention. cannot do much about return expressions.
            return ail_graph

        # Block walker

        def _handle_Return(stmt_idx: int, stmt: ailment.Stmt.Return, block: Optional[ailment.Block]):  # pylint:disable=unused-argument
            if block is not None \
                    and not stmt.ret_exprs \
                    and self.function.calling_convention.ret_val is not None:
                new_stmt = stmt.copy()
                ret_val = self.function.calling_convention.ret_val
                if isinstance(ret_val, SimRegArg):
                    reg = self.project.arch.registers[ret_val.reg_name]
                    new_stmt.ret_exprs.append(ailment.Expr.Register(None, None, reg[0],
                                                                    reg[1] * self.project.arch.byte_width))
                else:
                    l.warning("Unsupported type of return expression %s.",
                              type(self.function.calling_convention.ret_val))
                block.statements[stmt_idx] = new_stmt


        def _handler(block):
            walker = AILBlockWalker()
            # we don't need to handle any statement besides Returns
            walker.stmt_handlers.clear()
            walker.expr_handlers.clear()
            walker.stmt_handlers[ailment.Stmt.Return] = _handle_Return
            walker.walk(block)

        # Graph walker

        AILGraphWalker(ail_graph, _handler, replace_nodes=True).walk()

        return ail_graph