    def __init__(self, stmt, context):
        self.stmt = stmt
        self.context = context
        self.stmt_table = {
            ast.Expr: self.expr,
            ast.Pass: self.parse_pass,
            ast.AnnAssign: self.ann_assign,
            ast.Assign: self.assign,
            ast.If: self.parse_if,
            ast.Call: self.call,
            ast.Assert: self.parse_assert,
            ast.For: self.parse_for,
            ast.AugAssign: self.aug_assign,
            ast.Break: self.parse_break,
            ast.Continue: self.parse_continue,
            ast.Return: self.parse_return,
            ast.Delete: self.parse_delete,
            ast.Str: self.parse_docblock  # docblock
        }
        stmt_type = self.stmt.__class__
        if stmt_type in self.stmt_table:
            lll_node = self.stmt_table[stmt_type]()
            self.lll_node = lll_node
        elif isinstance(stmt, ast.Name) and stmt.id == "throw":
            self.lll_node = LLLnode.from_list(['assert', 0], typ=None, pos=getpos(stmt))
        else:
            raise StructureException("Unsupported statement type: %s" % type(stmt), stmt)