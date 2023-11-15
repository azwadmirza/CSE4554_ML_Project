    def check_partial(self, node: Union[FuncDef,
                                        LambdaExpr,
                                        MypyFile,
                                        OverloadedFuncDef]) -> None:
        if isinstance(node, MypyFile):
            self.check_top_level(node)
        else:
            self.recurse_into_functions = True
            if isinstance(node, LambdaExpr):
                self.expr_checker.accept(node)
            else:
                self.accept(node)