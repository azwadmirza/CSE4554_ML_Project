    def name_already_defined(self, name: str, ctx: Context,
                             original_ctx: Optional[SymbolTableNode] = None) -> None:
        if original_ctx:
            extra_msg = ' on line {}'.format(original_ctx.node.get_line())
        else:
            extra_msg = ''
        self.fail("Name '{}' already defined{}".format(name, extra_msg), ctx)